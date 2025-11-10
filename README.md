# Helvox

**Helvox** is an open-source GUI application for recording audio data in Swiss German dialects.  
It provides a simple and efficient interface for collecting high-quality speech recordings, making it ideal for linguistic research, dataset creation, and dialect analysis.

---

## Features

- Record and save high-quality audio clips
- Tailored for Swiss German dialect data collection
- Built with Python and modern audio libraries
- Cross-platform (developed primarily for Windows)
- Automatic voice activity detection for consistent recordings

---

## Dependencies

Helvox relies on a few core Python libraries for audio capture, processing, and platform management:

```bash
sounddevice
soundfile
platformdirs
webrtcvad
```

These dependencies will be installed automatically when setting up the project.

---

## Development Setup

To run Helvox locally in development mode:

```bash
pip install -e .
python -m helvox
```

or just simply run:

```bash
helvox
```

This will start the Helvox GUI application.

---

## Build Instructions (Windows)

To create a standalone executable for Windows:

```bash
pip install -e ".[build]"
pyinstaller windows.spec
```

After building, your packaged application will be available at:

```
dist/Helvox.exe
```

---

## Contributing

Contributions are welcome.
If you’d like to improve Helvox or add new features:

1. Fork this repository
2. Create a new branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to your fork: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

Helvox was built to support data collection and research in Swiss German linguistics.
Special thanks to all contributors and researchers working on dialect preservation and computational linguistics.
