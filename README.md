# 📘 ebook reader

A Python-based e-paper display **emulator** for a Raspberry Pi eBook project. This tool simulates how your UI and book navigation would look on a real e-paper device—ideal for development and testing on Windows before deploying to real hardware.
This emulator mimics the menu system and display behavior of an e-paper-based eBook reader controlled via GPIO buttons. It allows fast iteration without needing a physical Raspberry Pi or display connected.

## ▶️ How to Run (Windows)

1. First-time setup:
setup_env.bat

2. To run the emulator:
run.bat

That's it — a test window should appear simulating the e-paper screen with basic menu navigation.
Other files (e.g., emulator-specific UI modules) are only for development and can be excluded from the device build.

## ✅ Features

- EPUB browsing and selection
- Menu-based navigation
- E-paper display rendering (simulated)
- GPIO-style input emulation

## 🛠 For Real Raspberry Pi Use

To deploy to a physical Raspberry Pi:
- Exclude emulator files
- Replace emulator input handling (WIP)
- Use an actual e-paper driver (e.g., Waveshare libraries)

---

**Author:** Arturrno, kamilceglarski, antosiowsky  
**License:** MIT
