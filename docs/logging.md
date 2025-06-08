# Logging System

The Adaptive EQ application includes a comprehensive logging system to help troubleshoot issues and understand application behavior.

## Log Levels

The following log levels are available (from most to least verbose):

1. `debug` - Detailed debugging information
2. `info` - General information about application flow
3. `warning` - Indicates potential issues that don't prevent the application from running
4. `error` - Error conditions that affect specific functionality
5. `critical` - Critical errors that may prevent the application from running

## Log File Location

Logs are stored in:
```
~/.cache/adaptive-eq/logs/adaptive-eq_YYYY-MM-DD.log
```

A new log file is created for each day.

## Setting Log Level

You can set the log level using the `ADAPTIVE_EQ_LOG_LEVEL` environment variable:

```bash
# Run with debug logging
ADAPTIVE_EQ_LOG_LEVEL=debug ./run.sh

# Run AppImage with debug logging
ADAPTIVE_EQ_LOG_LEVEL=debug ./Adaptive_EQ-x86_64.AppImage
```

If not specified, the default level is `info`.

## Log Format

Log messages in the file have the format:
```
TIMESTAMP - MODULE_NAME - LEVEL - MESSAGE
```

Example:
```
2025-06-08 15:42:31,123 - services.eq_control - ERROR - Failed to apply preset 'rock': Command failed
```

## Using Logs for Troubleshooting

When reporting issues, please include relevant log files to help diagnose the problem. You can increase the log level to `debug` to get more detailed information.

### Common Log Messages

#### Spotify Connection
- "Spotify authentication error" - Check your Spotify credentials
- "Could not obtain Spotify client" - Network or authentication issue
- "Using cached track information" - Offline fallback mode

#### EQ Control
- "Failed to apply preset" - Problem with EasyEffects/PulseEffects
- "Successfully applied EasyEffects preset" - EQ preset successfully applied
- "No EasyEffects or PulseEffects presets found" - Missing EQ presets

#### Startup
- "PyGObject (GTK) is not installed" - Missing GTK dependencies
- "AppIndicator3 is not properly configured" - Missing AppIndicator dependencies
