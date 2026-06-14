# Video Compressor 🎥

![Cover photo](/icon-256.png)

A native, lightweight macOS desktop application that performs mathematically **lossless video compression** using FFmpeg. Built with Python, Tkinter, and `tkinterdnd2`, it features a modern dark-themed GUI, drag-and-drop support, and a live visual progress indicator.

## ✨ Features
* **100% Lossless Compression:** Uses `libx264` with `-crf 0` to compress videos mathematically without losing a single pixel of quality.
* **Streamlined Drag & Drop:** Drag files directly from macOS Finder into the app window, or onto the application Dock icon.
* **Modern Dark UI:** Clean, minimalistic interface with an animated circular progress loader and success triggers.
* **Audio Preservation:** Audio streams are copied exactly (`-c:a copy`) to guarantee zero quality degradation.

---

## 🚀 Prerequisites

To run or build this application, the host Mac must have **FFmpeg** installed via Homebrew.

1. **Install Homebrew** (if you don't have it):
   ```bash
   /bin/bash -c "$(curl -fsSL https://githubusercontent.com)"
   ```
2. **Install FFmpeg**:
   ```bash
   brew install ffmpeg
   ```

---

## 💾 Quick Download (No Coding Required)

If you just want to use the app without setting up a development environment:

1. Go to the [**Latest Release**](https://github.com/yashrajbharti/Video-Compressor/releases/tag/1.0.0).
2. Download the `Video Compressor.zip` file.
3. Unzip the file and move the `Video Compressor.app` to your **Applications** folder.

*Note: You still need to have FFmpeg installed on your Mac (`brew install ffmpeg`) for the app to process videos behind the scenes.*

### ⚠️ First-Time Launch (Bypassing macOS Gatekeeper)

Because this app is compiled locally and not signed with a paid Apple Developer certificate, modern macOS versions will show an alert with only two choices: **"Done"** or **"Move to Bin"**.

To open the app safely without moving it to the trash:
1. Double-click the app, see the warning, and click **Done** to dismiss the box.
2. Go to your Mac's **System Settings** -> **Privacy & Security**.
3. Scroll down to the very bottom to the **Security** section.
4. Look for the message saying *"Video Compressor was blocked..."* and click **Open Anyway**.
5. Type your Mac user password to grant permission. 
6. *You only have to do this once.* The app will now open normally by double-clicking it in the future!


## 🛠️ Development Setup & Installation

If you want to run the source code directly or modify the interface, clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com
cd video-compressor

# Install dependencies
pip3 install tkinterdnd2 setuptools py2app
```

### Running the App from Source
```bash
python3 app.py
```

---

## 📦 How to Build the macOS `.app` Bundle

You can compile the Python script into a native, standalone macOS application package (`.app`) using `py2app`.

1. Ensure your `setup.py` contains the correct build parameters:
   ```python
   OPTIONS = {
       'iconfile': 'icon.icns',
       'argv_emulation': True,
       'packages': ['tkinterdnd2']
   }
   ```
2. Run the compiler command in your terminal:
   ```bash
   # Clear out old builds and recompile
   rm -rf build dist
   python3 setup.py py2app
   ```
3. Your compiled app will appear inside the **`dist/`** directory as `Video Compressor.app`.

---

## 🤝 Sharing with Other Mac Users

Because the application is built locally and isn't digitally signed with an Apple Developer Account, macOS Gatekeeper will throw an "unidentified developer" warning on other machines.

**Instructions for recipients:**
1. Right-click the distributed `.app` package (or its extracted `.zip`) and select **Open**.
2. Click **Open Anyway** on the security pop-up prompt. 
3. *Note: This step is only required on the very first launch.*
4. Ensure **FFmpeg** is installed on their machine (`brew install ffmpeg`).

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
