# helvox

### Development
```bash
pip install -e .
python -m helvox
```

### Build (Windows):

```bash
pip install -e ".[build]"

pyinstaller windows.spec
```

Output will be in: `dist/Helvox.exe`