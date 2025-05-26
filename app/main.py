#!/usr/bin/env python3 
import os
import sys
import time
import zipfile
import textwrap
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import platform
import json
from battery_monitor import calculate_battery_percentage, read_battery_voltage 
from button_pressed import is_button_pressed

# Set up e-paper display
if platform.system() == "Windows":
    from mock_epd import MockEPD as EPD
    epd = EPD()
    runningDir = os.path.dirname(os.path.abspath(__file__))
    bookshelfPath = os.path.join(runningDir, "Bookshelf")
else:
    from waveshare_epd import epd7in5_V2
    EPD = epd7in5_V2.EPD
    epd = epd7in5_V2.EPD()
    runningDir = "/home/pi"
    bookshelfPath = "/home/pi/Bookshelf"

# Set up book progress tracking
progress_path = os.path.join(runningDir, "reading_progress.json")
if os.path.exists(progress_path):
    with open(progress_path, 'r') as f:
        reading_progress = json.load(f)
else:
    reading_progress = {}

# Initialize the e-paper display
epd.init()
epd.Clear()

# GPIO pins
BUTTON_UP = 16
BUTTON_DOWN = 6
BUTTON_RIGHT = 19
BUTTON_LEFT = 21

# Constants
width, height = 480, 800
BLACK, WHITE = 0, 255

MENU_ITEMS = ["Czytaj książkę", "Rozmiar czcionki", "Czcionka", "Wyłącz urządzenie"]
MENU_ITEM_HEIGHT, MENU_PADDING = 50, 10
FM_ITEM_HEIGHT, FM_PADDING = 40, 10
RD_STATUS_BAR_HEIGHT, RD_TOP_MARGIN = 40, 50
RD_BOTTOM_MARGIN, RD_SIDE_MARGIN = 20, 20
RD_LINE_SPACING, RD_CHARS_PER_LINE = 8, 40

FONT_SIZES = [18, 22, 26, 30]
DEFAULT_FONT_SIZE = 22
settings = {
    'font_name': 'DejaVuSans.ttf',
    'font_size': DEFAULT_FONT_SIZE,
    'last_book': None
}

fontDirectory = os.path.join(runningDir, "Fonts")
fontPath = os.path.join(fontDirectory, settings['font_name'])
if not os.path.exists(fontPath):
    print(f"Font file not found: {fontPath}")
    sys.exit(1)

available_fonts = sorted([f for f in os.listdir(fontDirectory) if f.lower().endswith('.ttf')])

# Utility function for loading fonts
def load_font(font_name, font_size):
    try:
        return ImageFont.truetype(os.path.join(fontDirectory, font_name), font_size)
    except:
        return ImageFont.load_default()

# Status font
status_font = load_font(settings['font_name'], 14)

# Base screen with shared display logic
class Screen:
    def __init__(self, app):
        self.app = app

    def update_display(self, image, partial=False):
        if partial:
            self.app.epd.init_part()
        else:
            self.app.epd.init()

        rotated_image = image.rotate(0)
        self.app.epd.display(self.app.epd.getbuffer(rotated_image))

    def draw_top_bar(self, image, screen_name=""):
        draw = ImageDraw.Draw(image)
        bar_height = 30
        padding = 10
        font = load_font(settings['font_name'], settings['font_size'])
        bold_font = font  # or define/load a bold variant

        # Font metrics for vertical centering
        ascent, descent = font.getmetrics()
        text_height = ascent + abs(descent)

        # Battery 
        battery_pct = calculate_battery_percentage(read_battery_voltage())

        battery_text = f"{battery_pct}%"
        battery_text_width = draw.textlength(battery_text, font=bold_font)
        battery_logo_width = 20
        battery_logo_height = 12
        battery_y = (bar_height - battery_logo_height) // 2
        battery_x = width - padding - battery_logo_width - battery_text_width - 8

        # Battery percentage text
        draw.text((battery_x, ((bar_height - text_height) // 2) + 1), battery_text, font=bold_font, fill=BLACK)

        # Battery icon
        icon_x = battery_x + battery_text_width + 5
        batt_top = battery_y
        batt_left = icon_x
        batt_right = icon_x + battery_logo_width
        batt_bottom = battery_y + battery_logo_height

        # Battery outline
        draw.rectangle((batt_left, batt_top, batt_right, batt_bottom), outline=BLACK, width=1)

        # Battery fill (based on %)
        fill_margin = 2
        fill_left = batt_left + fill_margin
        fill_right = batt_right - fill_margin
        fill_top = batt_top + fill_margin
        fill_bottom = batt_bottom - fill_margin

        fill_width = int((fill_right - fill_left) * (battery_pct / 100))
        if fill_width > 0:
            draw.rectangle((fill_left, fill_top, fill_left + fill_width, fill_bottom), fill=BLACK)

        # Battery tip
        draw.rectangle((batt_right, batt_top + 3, batt_right + 3, batt_bottom - 3), fill=BLACK)


        # Wi-Fi signal bars (empty outline)
        wifi_x = battery_x - 45
        wifi_bar_width = 3
        wifi_bar_height = 18
        wifi_y_top = (battery_y + batt_bottom - wifi_bar_height)/2
        wifi_spacing = 2

        # Draw the outline for each of the 4 Wi-Fi bars
        for i in range(4):
            bar_x = wifi_x + i * (wifi_bar_width + wifi_spacing)
            bar_top = wifi_y_top + ((3 - i) / 4) * wifi_bar_height
            bar_bottom = wifi_y_top + wifi_bar_height
            draw.rectangle((bar_x, bar_top, bar_x + wifi_bar_width, bar_bottom), outline=BLACK, width=1)

        # Fill Wi-Fi bars based on signal strength
        signal_strength = 77  # This will need to return signal strength (0-100%)
        filled_bars = int(signal_strength / 25)  # Split signal strength into 4 parts

        for i in range(filled_bars):
            bar_x = wifi_x + i * (wifi_bar_width + wifi_spacing)
            bar_top = wifi_y_top + ((3 - i) / 4) * wifi_bar_height
            bar_bottom = wifi_y_top + wifi_bar_height
            draw.rectangle((bar_x, bar_top, bar_x + wifi_bar_width, bar_bottom), fill=BLACK)

        # Screen title (left aligned)
        title_text = screen_name
        draw.text((padding, (bar_height - text_height) // 2), title_text, font=font, fill=BLACK)

        # Separator line
        draw.line((0, bar_height, width, bar_height), fill=BLACK)


class StartupAnimationScreen(Screen):
    def __init__(self, app):
        super().__init__(app)

    def run(self):
        # Load and resize logo image
        logo = Image.open(os.path.join(runningDir,"logo.png")).convert('1')
        base_image = logo.resize((width, height))

        self.update_display(base_image, True)

        time.sleep(1)
        self.update_display(self.app.empty_image, partial=False)

# Menus
class MenuScreen(Screen):
    def handle_input(self, key): pass
    def run(self): pass

class MainMenu(MenuScreen):
    def __init__(self, app):
        super().__init__(app)
        self.selected_idx = 0

    def get_menu_image(self):
        image = self.app.empty_image.copy()
        draw = ImageDraw.Draw(image)

        # Draw the top bar with screen name
        self.draw_top_bar(image, screen_name="Menu")

        # Shift content down below the top bar
        y_offset = MENU_PADDING + 30  # Add space for top bar

        start = max(0, self.selected_idx - self.visible_items() // 2)
        end = min(len(MENU_ITEMS), start + self.visible_items())

        for i in range(start, end):
            if i == self.selected_idx:
                draw.rectangle((MENU_PADDING, y_offset, width - MENU_PADDING, y_offset + MENU_ITEM_HEIGHT), outline=BLACK)
            draw.text((2*MENU_PADDING, y_offset + 15), MENU_ITEMS[i], font=load_font(settings['font_name'], settings['font_size']), fill=BLACK)
            y_offset += MENU_ITEM_HEIGHT

        return image

    def visible_items(self):
        # Adjust for the top bar
        return (height - 2*MENU_PADDING - 30) // MENU_ITEM_HEIGHT

    def handle_input(self, key):
        if key == 'w' and self.selected_idx > 0:
            self.selected_idx -= 1
        elif key == 's' and self.selected_idx < len(MENU_ITEMS) - 1:
            self.selected_idx += 1
        elif key == '':
            if self.selected_idx == 0:
                self.app.current_mode = "file_manager"
            elif self.selected_idx == 1:
                self.app.current_mode = "font_size_menu"
            elif self.selected_idx == 2:
                self.app.current_mode = "font_choice_menu"
            elif self.selected_idx == 3:
                self.app.epd.sleep()
                sys.exit(0)
            return True
        return True

    def run(self):
        prev_idx = -1
        while True:
            if self.selected_idx != prev_idx:
                self.update_display(self.get_menu_image(), partial=True)
                prev_idx = self.selected_idx

            print("\nWybierz opcję: [w/s] góra/dół, [Enter] wybór")
            #key = input("Wybierz: ")
            #if self.handle_input(key.lower().strip()):
            #   break

            if is_button_pressed(BUTTON_UP):
                self.handle_input('w')
            elif is_button_pressed(BUTTON_DOWN):
                self.handle_input('s')
            elif is_button_pressed(BUTTON_RIGHT):
                if self.handle_input(''):
                    break

class SettingsMenu(MenuScreen):
    def __init__(self, app):
        super().__init__(app)
        self.selected_idx = FONT_SIZES.index(settings['font_size'])

    def get_font_size_image(self):
        image = self.app.empty_image.copy()
        draw = ImageDraw.Draw(image)

        y_offset = MENU_PADDING + 30
        self.draw_top_bar(image, screen_name="Rozmiar czcionki")

        for i, size in enumerate(FONT_SIZES):
            if i == self.selected_idx:
                draw.rectangle((MENU_PADDING, y_offset, width - MENU_PADDING, y_offset + MENU_ITEM_HEIGHT), outline=BLACK)
            draw.text(
                (2*MENU_PADDING, y_offset + 15),
                f"Rozmiar {size}px",
                font=load_font(settings['font_name'], size),
                fill=BLACK
            )
            y_offset += MENU_ITEM_HEIGHT

        draw.text((MENU_PADDING, height - 30), "Enter: wybierz  q: powrót", font=status_font, fill=BLACK)
        return image

    def handle_input(self, key):
        if key == 'w' and self.selected_idx > 0:
            self.selected_idx -= 1
        elif key == 's' and self.selected_idx < len(FONT_SIZES) - 1:
            self.selected_idx += 1
        elif key == '':
            settings['font_size'] = FONT_SIZES[self.selected_idx]
            self.app.current_mode = "main_menu"
            return True
        elif key == 'q':
            self.app.current_mode = "main_menu"
            return True
        return False

    def font_size_menu(self):
        prev = -1
        while True:
            if self.selected_idx != prev:
                self.update_display(self.get_font_size_image(), partial=True)
                prev = self.selected_idx
            print("\nWybierz rozmiar: [w/s] wybór, [Enter] zatwierdź, [q] powrót")
            if self.handle_input(input("Wybierz: ").lower().strip()):
                break

class FontMenu(MenuScreen):
    def __init__(self, app):
        super().__init__(app)
        self.fonts = available_fonts
        self.selected_idx = self.fonts.index(settings['font_name']) if settings['font_name'] in self.fonts else 0

    def get_font_choice_image(self):
        image = self.app.empty_image.copy()
        draw = ImageDraw.Draw(image)

        self.draw_top_bar(image, screen_name="Czcionka")
        y_offset = MENU_PADDING + 30
        for i, font_name in enumerate(self.fonts):
            if i == self.selected_idx:
                draw.rectangle((MENU_PADDING, y_offset, width - MENU_PADDING, y_offset + MENU_ITEM_HEIGHT), outline=BLACK)
            draw.text(
                (2*MENU_PADDING, y_offset + 15),
                font_name,
                font=load_font(font_name, settings['font_size']),
                fill=BLACK
            )
            y_offset += MENU_ITEM_HEIGHT

        draw.text((MENU_PADDING, height - 30), "Enter: wybierz  q: powrót", font=status_font, fill=BLACK)
        return image

    def handle_input(self, key):
        if key == 'w' and self.selected_idx > 0:
            self.selected_idx -= 1
        elif key == 's' and self.selected_idx < len(self.fonts) - 1:
            self.selected_idx += 1
        elif key == '':
            settings['font_name'] = self.fonts[self.selected_idx]
            self.app.current_mode = "main_menu"
            return True
        elif key == 'q':
            self.app.current_mode = "main_menu"
            return True
        return False
    
    def font_choice_menu(self):
        prev = -1
        while True:
            if self.selected_idx != prev:
                self.update_display(self.get_font_choice_image(), partial=True)
                prev = self.selected_idx
            print("\nWybierz czcionkę: [w/s] wybór, [Enter] zatwierdź, [q] powrót")
            if self.handle_input(input("Wybierz: ").lower().strip()):
                break

# File manager
class FileManager(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.files = self.list_ebooks(bookshelfPath)
        self.selected_idx = 0

    def list_ebooks(self, directory):
        return sorted([f for f in os.listdir(directory) if f.lower().endswith(('.epub', '.pdf'))])

    def get_file_image(self):
        image = self.app.empty_image.copy()
        draw = ImageDraw.Draw(image)

        self.draw_top_bar(image, screen_name="Wybór książki")

        y_offset = FM_PADDING + 30  # Add space for top bar

        start = max(0, self.selected_idx - self.max_items() // 2)
        end = min(len(self.files), start + self.max_items())

        for i in range(start, end):
            if i == self.selected_idx:
                draw.rectangle((FM_PADDING, y_offset, width - FM_PADDING, y_offset + FM_ITEM_HEIGHT), outline=BLACK)
            name = self.files[i][:27] + "..." if len(self.files[i]) > 30 else self.files[i]
            draw.text((2*FM_PADDING, y_offset + 10), name, font=load_font(settings['font_name'], settings['font_size']), fill=BLACK)
            y_offset += FM_ITEM_HEIGHT
        draw.text((FM_PADDING, height - 30), "W/S: wybierz  Enter: otwórz  q: powrót", font=status_font, fill=BLACK)
        return image

    def max_items(self):
        return (height - 2*FM_PADDING) // FM_ITEM_HEIGHT

    def handle_input(self, key):
        if key == 'w' and self.selected_idx > 0:
            self.selected_idx -= 1
        elif key == 's' and self.selected_idx < len(self.files) - 1:
            self.selected_idx += 1
        elif key == '':
            filepath = os.path.join(bookshelfPath, self.files[self.selected_idx])
            settings['last_book'] = filepath
            self.app.reader.load_epub(filepath)
            self.app.current_mode = "reader"
            return True
        elif key == 'q':
            self.app.current_mode = "main_menu"
            return True
        return True

    def run(self):
        prev_idx = -1
        while True:
            if self.selected_idx != prev_idx:
                self.update_display(self.get_file_image(), partial=True)
                prev_idx = self.selected_idx
            print("\nWybierz książkę: [w/s] góra/dół, [Enter] otwórz, [q] powrót")
            if self.handle_input(input("Wybierz: ").lower().strip()):
                break

# Reader
class Reader(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.pages, self.current_page, self.total_pages = [], 0, 0
        self.current_book_path = None

    def save_progress(self, book_path):
        reading_progress[book_path] = self.current_page
        with open(progress_path, 'w') as f:
            json.dump(reading_progress, f)

    def load_epub(self, path):
        full_paragraphs = []

        self.current_book_path = path

        with zipfile.ZipFile(path, 'r') as epub:
            # Parse container.xml to get OPF path
            with epub.open('META-INF/container.xml') as f:
                container = BeautifulSoup(f.read(), 'xml')
                opf_path = container.rootfiles.rootfile['full-path']

            opf_dir = os.path.dirname(opf_path)
            with epub.open(opf_path) as f:
                opf = BeautifulSoup(f.read(), 'xml')

            # Get spine-based reading order
            item_map = {item['id']: item['href'] for item in opf.find_all('item') if 'application/xhtml+xml' in item.get('media-type', '')}
            spine_ids = [item['idref'] for item in opf.find_all('itemref')]

            for idref in spine_ids:
                href = item_map.get(idref)
                if not href:
                    continue
                
                path_in_zip = f"{opf_dir}/{href}" if opf_dir else href

                with epub.open(path_in_zip) as f:
                    html = BeautifulSoup(f.read(), 'html.parser')
                    for tag in html(['header', 'footer', 'nav', 'script', 'style']):
                        tag.decompose()
                    paragraphs = [p.get_text(strip=True) for p in html.find_all(['p', 'div']) if p.get_text(strip=True)]
                    full_paragraphs.extend(paragraphs)

        # Text layout
        dummy_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        font = load_font(settings['font_name'], settings['font_size'])
        line_height = font.getbbox("A")[3] + RD_LINE_SPACING
        lines_per_page = (height - RD_TOP_MARGIN - RD_BOTTOM_MARGIN) // line_height
        max_width = width - 2 * RD_SIDE_MARGIN

        self.pages = []
        current_lines = []

        for para in full_paragraphs:
            words = para.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                if draw.textlength(test_line, font=font) <= max_width:
                    line = test_line
                else:
                    current_lines.append(line)
                    line = word
            if line:
                current_lines.append(line)
            current_lines.append("")  # paragraph break

            while len(current_lines) >= lines_per_page:
                self.pages.append("\n".join(current_lines[:lines_per_page]))
                current_lines = current_lines[lines_per_page:]

        if current_lines:
            self.pages.append("\n".join(current_lines))

        self.current_page = 0

        # Resume from saved page if available
        if path in reading_progress:
            saved_page = reading_progress[path]
            if 0 <= saved_page < self.total_pages:
                self.current_page = saved_page

        self.total_pages = len(self.pages)

    def get_page_image(self):
        image = self.app.empty_image.copy()
        draw = ImageDraw.Draw(image)
        font = load_font(settings['font_name'], settings['font_size'])

        # Top bar
        draw.rectangle((0, 0, width, RD_STATUS_BAR_HEIGHT), fill=WHITE, outline=BLACK)
        page_info = f"{self.current_page+1}/{self.total_pages}"
        draw.text((RD_SIDE_MARGIN, 10), page_info, font=status_font, fill=BLACK)

        battery_info = calculate_battery_percentage(read_battery_voltage()) + "%"
        battery_width = draw.textlength(battery_info, font=status_font)
        draw.text((width - RD_SIDE_MARGIN - battery_width, 10), battery_info, font=status_font, fill=BLACK)

        progress_width = width - 2 * RD_SIDE_MARGIN - draw.textlength(page_info, font=status_font) - battery_width - 20
        progress_x = RD_SIDE_MARGIN + draw.textlength(page_info, font=status_font) + 10
        progress = (self.current_page + 1) / self.total_pages
        draw.rectangle((progress_x, 17, progress_x + progress_width, 23), outline=BLACK)
        draw.rectangle((progress_x, 17, progress_x + int(progress_width * progress), 23), fill=BLACK)

        # Text body
        y = RD_TOP_MARGIN
        for line in self.pages[self.current_page].split('\n'):
            draw.text((RD_SIDE_MARGIN, y), line, font=font, fill=BLACK)
            line_height = font.getbbox("A")[3] + RD_LINE_SPACING
            y += line_height
        return image

    def handle_input(self, key):
        if key == 'a' and self.current_page > 0:
            self.current_page -= 1
        elif key == 'd' and self.current_page < self.total_pages - 1:
            self.current_page += 1
        elif key in ['q', 'm']:
            self.app.current_mode = "main_menu"
            return True
        return True

    def run(self):
        prev = -1
        while True:
            if self.current_page != prev:
                self.update_display(self.get_page_image())
                prev = self.current_page
            print(f"\nStrona {self.current_page+1}/{self.total_pages}")
            print("[a/d] ←/→, [q/m] powrót/menu")
            if self.handle_input(input("Wybierz: ").lower().strip()):
                if self.app.current_mode == "main_menu":
                    break
            self.save_progress(self.app.reader.current_book_path)


# Main App
class EbookReader:
    def __init__(self):
        self.epd = epd
        self.empty_image = Image.new('1', (width, height), WHITE)
        self.current_mode = "main_menu"
        self.main_menu = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.file_manager = FileManager(self)
        self.reader = Reader(self)
        self.startup = StartupAnimationScreen(self)

    def run(self):
        try:
            self.startup.run()
            while True:
                if self.current_mode == "main_menu":
                    self.main_menu.run()
                if self.current_mode == "font_size_menu":
                    SettingsMenu(self).font_size_menu()
                elif self.current_mode == "font_choice_menu":
                    FontMenu(self).font_choice_menu()
                elif self.current_mode == "file_manager":
                    self.file_manager.run()
                elif self.current_mode == "reader":
                    self.reader.run()
        except KeyboardInterrupt:
            print("Zamykanie...")
        finally:
            self.epd.sleep()

if __name__ == "__main__":
    app = EbookReader()
    app.run()