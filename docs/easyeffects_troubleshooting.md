# EasyEffects Integration Troubleshooting

This guide addresses common issues with EasyEffects integration, particularly focusing on the UI synchronization problem where EQ presets don't visibly change in the EasyEffects interface.

## Understanding the Issue

EasyEffects can sometimes experience UI synchronization issues where:
- The sound changes correctly when presets are applied
- The EasyEffects UI doesn't update to show the current preset
- Preset changes are correctly registered in the system but not displayed

This can happen due to:
1. Race conditions in the EasyEffects UI update mechanism
2. Missing or corrupt configuration files
3. DBus communication issues
4. Different versions of EasyEffects handling preset changes differently

## Diagnosis and Solutions

### Run the Diagnostic Tool

```bash
./debug_easyeffects.py
```

This tool will:
- Check if EasyEffects is running
- Verify configuration files
- Test different preset application methods
- Provide real-time feedback on what works for your system

### Configuration File Issues

If EasyEffects doesn't have a proper `config.json` file, UI updates may fail:

1. Check if the file exists:
   ```bash
   ls -la ~/.config/easyeffects/config.json
   ```

2. If missing, create it manually:
   ```bash
   mkdir -p ~/.config/easyeffects
   echo '{
     "spectrum": {"show": "true"},
     "last-used-input-preset": "default",
     "last-used-output-preset": "default",
     "use-dark-theme": "true"
   }' > ~/.config/easyeffects/config.json
   ```

### Force Preset Application

If the UI still doesn't update, you can force a refresh:

```bash
./force_reload_presets.py <preset_name>
```

Replace `<preset_name>` with the name of the preset you want to apply.

### EasyEffects Version Differences

Different versions of EasyEffects may require different approaches:

1. **EasyEffects 6.x and newer**:
   - Primarily uses gsettings and DBus
   - UI issues are less common but can still occur

2. **EasyEffects 5.x**:
   - May require file-based approach
   - Check if preset directory is at `~/.config/easyeffects/output/`

3. **PulseEffects (legacy version)**:
   - Check for presets in `~/.config/PulseEffects/output/`
   - May require different DBus interface

### Running with Force-Refresh

For persistent UI issues, you can run Adaptive EQ with force-refresh enabled:

```bash
./run_cli.sh
```

Or directly:

```bash
python3 main.py --force-refresh
```

This mode will:
- Apply presets using multiple methods
- Periodically force a UI refresh
- Use more aggressive measures to ensure the UI stays in sync

## Manual Intervention

If all automatic methods fail, you can try these steps:

1. **Restart EasyEffects**:
   ```bash
   killall easyeffects
   easyeffects &
   ```

2. **Reset EasyEffects configuration**:
   ```bash
   mv ~/.config/easyeffects ~/.config/easyeffects.bak
   ```
   Then restart EasyEffects.

3. **Check DBus interface**:
   ```bash
   dbus-send --session --print-reply --dest=com.github.wwmm.easyeffects \
     /com/github/wwmm/easyeffects org.freedesktop.DBus.Introspectable.Introspect
   ```
   This should return a valid DBus interface description.

4. **Verify gsettings**:
   ```bash
   gsettings get com.github.wwmm.easyeffects last-used-output-preset
   ```
   This should return the name of the current preset.

## Prevention Measures

To prevent UI sync issues:

1. Start EasyEffects before starting Adaptive EQ
2. Ensure you have the latest version of EasyEffects
3. Use the tray application which includes the force-refresh option
4. Consider running EasyEffects as a background service:
   ```bash
   easyeffects --gapplication-service &
   ```

## Additional Resources

- [EasyEffects GitHub repository](https://github.com/wwmm/easyeffects)
- [DBus Interface Documentation](https://dbus.freedesktop.org/doc/dbus-specification.html)
- [GSetting Documentation](https://developer.gnome.org/GSettings/)
