## Features in the Tray Application

- View currently playing track
- Toggle adaptive mode on/off
- Manually select EQ presets
- Refresh EQ profiles
- Create new EQ presets
- Configure Spotify
- Easy access to quit the application

## Advanced Features

### Logging System

The application now includes a comprehensive logging system that helps with troubleshooting:

- Logs are stored in `~/.cache/adaptive-eq/logs/`
- Log level can be set with environment variable: `ADAPTIVE_EQ_LOG_LEVEL=debug ./run.sh`
- Log levels: debug, info, warning, error, critical

### Fallback Mechanisms

The application includes several fallback mechanisms:

1. **EQ Control**: Multiple methods to apply EQ presets (gsettings, dbus, file copy)
2. **Offline Mode**: Cached track information when Spotify is unavailable
3. **Preset Detection**: Checks multiple locations for EasyEffects/PulseEffects presets
4. **Configuration**: Automatically creates default configuration if not found

### Distribution Compatibility

The application is designed to work across multiple Linux distributions:

- Debian/Ubuntu/Mint
- Fedora/RHEL/CentOS
- Arch Linux/Manjaro
- openSUSE
- Other distributions should work with minimal adjustments
