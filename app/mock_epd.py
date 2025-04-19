import tkinter as tk
from PIL import Image, ImageTk

class MockEPD:
    width = 480
    height = 800

    def __init__(self):
        self.image = Image.new('1', (self.width, self.height), 255)  # White image
        self.image_showed = False
        self.root = None
        self.canvas = None

    def init(self):
        print("MockEPD: init")
        self.image = Image.new('1', (self.width, self.height), 255)  # Default blank white image
        self.image_showed = True

    def init_part(self):
        print("MockEPD: partial init")
        self.image = Image.new('1', (self.width, self.height), 255)  # Default blank white image
        self.image_showed = True

    def Clear(self):
        print("MockEPD: clear")
        self.image = Image.new('1', (self.width, self.height), 255)  # Clear to white
        self.image_showed = False
        self.update_display()

    def getbuffer(self, image):
        return image

    def display(self, image):
        if image != self.image:
            self.image = image
        print("MockEPD: display updated")
        
        self.update_display()

    def update_display(self):
        if not self.image_showed:
            # Create a Tkinter window to display the image for the first time
            self.root = tk.Tk()
            self.root.title("Mock EPD Display")
            
            # Create a Canvas to display the image
            self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
            self.canvas.pack()

            self.image_showed = True
        
        # Convert PIL image to Tkinter-compatible format
        photo = ImageTk.PhotoImage(self.image)

        # Update the image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)

        # Keep reference to avoid garbage collection
        self.canvas.image = photo

        # Refresh the window to show the updated image
        self.root.update()

    def sleep(self):
        print("MockEPD: sleep")
        if self.root:
            self.root.quit()  # Close the Tkinter window
