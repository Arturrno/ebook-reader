# 📘 eBook Reader Emulator

A Python-based **e-paper display emulator** for a Raspberry Pi eBook reader project. This tool allows you to **simulate the UI and navigation** of a real e-paper device directly on Windows — perfect for testing before deploying to hardware.

---

## 🧠 Project Overview

This emulator mimics:
- E-paper display rendering
- Menu-driven EPUB browsing
- GPIO-style input handling (via keyboard)
  
It's especially useful for fast development without needing:
- Raspberry Pi hardware
- A connected e-paper screen

---

## ⚙️ Hardware Target

This emulator is designed for a real hardware setup based on:

- 📟 **Raspberry Pi Zero 2 W**
- 🖼️ **7.5" E-paper Display**
- 🔋 **4000 mAh Battery**

In the future, this emulator will be fully replaceable with real GPIO inputs and Waveshare e-paper drivers for actual deployment.

---

## ▶️ How to Run (Windows)

### 1. First-time Setup
```bash
setup_env.bat
```

This installs the required virtual environment and dependencies.

### 2. Start the Emulator
```bash
run.bat
```

A test window should open, simulating the e-paper screen and navigation system.

> ℹ️ The emulator UI and logic are modular — they can be replaced or excluded for the real hardware version.

---

## ✅ Features

- 📖 EPUB file browsing and book selection
- 🧭 Menu-based navigation
- 🖼️ Simulated e-paper screen rendering
- 🎮 GPIO-style input emulation (mapped to keyboard for dev)

---

## 🛠️ Deploying to Real Raspberry Pi

To run this on real hardware:

- 🔥 **Exclude** emulator-specific files (UI, input emulation, etc.)
- 🧩 **Replace** emulator input handling with GPIO logic (WIP)
- 📦 Use a real e-paper driver (e.g., Waveshare Python libraries)

This part of the code is **in progress** — contributions welcome!

---

## 👨‍💻 Authors

- [Arturrno](https://github.com/Arturrno)  
- [kamilceglarski](https://github.com/kamilceglarski)  
- [antosiowsky](https://github.com/antosiowsky)

---

## 📄 License

MIT License — see [`LICENSE`](LICENSE) file for details.
