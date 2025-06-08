# GTK Dependencies Troubleshooting

If you're encountering errors related to missing Python GTK modules when running Adaptive EQ, this guide will help you resolve them.

## Common Error Messages

### `ModuleNotFoundError: No module named 'gi'`

This error occurs when the Python GTK bindings (PyGObject) are not installed on your system. The application uses these bindings to create its graphical user interface.

### `ImportError: cannot import name 'AppIndicator3'` or similar

This error occurs when the AppIndicator3 module is missing, which is required for the system tray functionality.

## Installing the Required Dependencies

Depending on your Linux distribution, you'll need to install different packages:

### Debian/Ubuntu-based Distributions

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

### Fedora/RHEL-based Distributions

```bash
sudo dnf install python3-gobject python3-cairo gtk3 libappindicator-gtk3
```

### Arch-based Distributions

```bash
sudo pacman -Sy python-gobject python-cairo gtk3 libappindicator-gtk3
```

## Verifying Installation

You can verify that the GTK bindings are correctly installed by running:

```bash
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK is installed')"
```

And for AppIndicator3:

```bash
python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); from gi.repository import AppIndicator3; print('AppIndicator3 is installed')"
```

## Within Virtual Environments

If you're using a virtual environment, you might need to install the system packages first and then make sure the virtual environment can access them:

1. Install the system packages as shown above
2. Make sure your virtual environment is created with `--system-site-packages` flag:
   ```bash
   python3 -m venv --system-site-packages system-venv
   ```

Or, if you're using an existing virtual environment:
1. Deactivate it first: `deactivate`
2. Recreate it with system packages: `python3 -m venv --system-site-packages system-venv`
3. Reinstall your Python dependencies: `pip install -r requirements.txt`

### Alternative Virtual Environment Approaches

1. **Using vext**:
   The vext package can allow access to specific system modules from within a virtual environment:
   ```bash
   pip install vext vext.gi
   ```

2. **Compiling PyGObject in your virtual environment**:
   This is more complex but allows for a fully isolated environment:
   
   On Debian/Ubuntu:
   ```bash
   sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
   pip install pycairo PyGObject
   ```
   
   On Fedora:
   ```bash
   sudo dnf install gobject-introspection-devel cairo-devel pkg-config python3-devel gtk3-devel
   pip install pycairo PyGObject
   ```
   
   On Arch Linux:
   ```bash
   sudo pacman -S gobject-introspection cairo pkgconf python gtk3
   pip install pycairo PyGObject
   ```

## Troubleshooting Common Issues

### PyGObject Import Error in Virtual Environment

If you receive an error like this inside a virtual environment:
```
ImportError: cannot import name '_gi' from 'gi'
```

It typically means the system GTK libraries are not accessible to your virtual environment. Try:

1. Recreate your environment with `--system-site-packages`
2. Check if you have development packages installed
3. Verify that your Python version in the virtual environment matches the version used by the system PyGObject

### Display Environment Variables

GTK applications may require proper display environment variables:

```bash
# Check your current display variable
echo $DISPLAY

# If empty, set it (usually for SSH sessions)
export DISPLAY=:0
```

## Additional Notes

- Python GTK bindings are not installable via pip alone, as they rely on system libraries
- If you're using a minimal distribution, you might need to install additional GTK libraries
- On some distributions, the package names might be slightly different
- Container environments (like Docker) need special handling for GTK applications
- WSL2 users need an X server on Windows to display GTK applications
