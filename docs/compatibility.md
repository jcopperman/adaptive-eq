# Compatibility Guide

Adaptive EQ is designed to work across multiple Linux distributions. This guide outlines the specific requirements and considerations for each supported distribution.

## Debian/Ubuntu/Mint

### Dependencies

```bash
# Install required dependencies
sudo apt install python3 python3-pip python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1

# Install EasyEffects (Ubuntu 22.04+, Debian 11+)
sudo apt install easyeffects

# OR for older versions (Ubuntu 20.04, Debian 10)
sudo apt install pulseeffects
```

### Special Considerations

- Ubuntu 18.04 and older may require additional PPAs for PulseEffects/EasyEffects
- Ubuntu 22.04+ uses PipeWire instead of PulseAudio, which works better with EasyEffects

## Fedora/RHEL/CentOS

### Dependencies

```bash
# Install required dependencies
sudo dnf install python3 python3-pip python3-gobject python3-cairo gtk3 libappindicator-gtk3

# Install EasyEffects
sudo dnf install easyeffects
```

### Special Considerations

- Fedora 34+ uses PipeWire by default, which works well with EasyEffects
- On CentOS/RHEL, you may need to enable EPEL repository

## Arch Linux/Manjaro

### Dependencies

```bash
# Install required dependencies
sudo pacman -Sy python python-pip python-gobject python-cairo gtk3 libappindicator-gtk3

# Install EasyEffects
sudo pacman -Sy easyeffects
```

### Special Considerations

- Arch users typically need the latest versions of libraries, which are well-supported

## openSUSE

### Dependencies

```bash
# Install required dependencies
sudo zypper install python3 python3-pip python3-gobject python3-cairo gtk3 libappindicator3-1

# Install EasyEffects
sudo zypper install easyeffects
```

## Universal Installation

The universal installer script (`install.sh`) will detect your distribution and install the appropriate dependencies. It's the recommended way to install Adaptive EQ:

```bash
./install.sh
```

## AppImage Compatibility

The AppImage package will work on any Linux distribution that has the necessary GTK libraries installed. The AppImage will check for required dependencies at startup and provide guidance if anything is missing.

## Troubleshooting Distribution-Specific Issues

### Debian/Ubuntu
- Missing AppIndicator: `sudo apt install gir1.2-appindicator3-0.1`
- Missing EasyEffects: On older systems, try `sudo apt install pulseeffects`

### Fedora
- SELinux may block some functionality: Try running in permissive mode or create appropriate SELinux policies

### Arch Linux
- Packages change frequently: Ensure your system is up-to-date with `sudo pacman -Syu`

### General
- If the application crashes on startup, check that all dependencies are installed
- Use the logging system to identify distribution-specific issues
