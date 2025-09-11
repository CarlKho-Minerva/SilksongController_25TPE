# Silksong Controller

A controller application for Hollow Knight: Silksong, combining Android mobile interface with Python backend processing.

## 🎮 Overview

This project provides a custom controller solution for Hollow Knight: Silksong, featuring:

- **Android App**: Mobile interface for game controls
- **Python Backend**: Game state processing and automation
- **Cross-platform Communication**: Seamless integration between mobile and desktop

## 🏗️ Project Structure

```text
SilksongController_25TPE/
├── AndroidStudio/          # Android mobile app
│   ├── app/               # Main Android application
│   ├── build.gradle.kts   # Build configuration
│   └── ...               # Android project files
├── python/                # Python backend (to be added)
├── docs/                  # Documentation
└── README.md             # This file
```

## 🚀 Getting Started

### Prerequisites

- **Android Development**:
  - Android Studio (latest version)
  - Android SDK 24+ (API level 24+)
  - Java 11 or higher

- **Python Development**:
  - Python 3.8+
  - pip package manager

### Installation

#### Android App Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/CarlKho-Minerva/SilksongController_25TPE.git
   cd SilksongController_25TPE
   ```

2. Open the Android project:

   ```bash
   cd AndroidStudio
   # Open in Android Studio
   ```

3. Build and run the Android app on your device or emulator

#### Python Backend Setup

1. Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## 📱 Features

### Current Features

- Basic Android app structure
- Gradle build configuration
- Modern Android development setup

### Planned Features

- [ ] Game controller interface
- [ ] Real-time input handling
- [ ] Python game state processing
- [ ] Network communication between app and backend
- [ ] Customizable control schemes
- [ ] Game automation features

## 🛠️ Development

### Android Development

The Android app is built using:

- **Language**: Kotlin
- **Minimum SDK**: API 24 (Android 7.0)
- **Target SDK**: Latest
- **Architecture**: Modern Android architecture components

### Python Development

The Python backend will use:

- **Framework**: TBD (FastAPI, Flask, or similar)
- **Communication**: WebSocket or REST API
- **Game Integration**: Input simulation libraries

## 📋 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Team Cherry for creating Hollow Knight: Silksong
- The Android and Python development communities
- Contributors and testers

## 📞 Contact

- **Developer**: CarlKho-Minerva
- **Repository**: [SilksongController_25TPE](https://github.com/CarlKho-Minerva/SilksongController_25TPE)

---

**Note**: This project is for educational and personal use. Please respect the game's terms of service and use responsibly.
