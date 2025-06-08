# Adaptive EQ Documentation

This directory contains detailed documentation for the Adaptive EQ application.

## Contents

- [Logging System](logging.md) - Details about the logging system, log levels, and troubleshooting
- [Compatibility Guide](compatibility.md) - Distribution-specific information and compatibility notes
- [EasyEffects Troubleshooting](easyeffects_troubleshooting.md) - Fixing issues with EasyEffects UI synchronization

## Additional Resources

- [FEATURES.md](../FEATURES.md) - Overview of advanced features and capabilities
- [README.md](../README.md) - Main documentation and usage instructions

## Troubleshooting

If you encounter issues with Adaptive EQ, please:

1. Check the [logging documentation](logging.md) and examine your log files
2. Verify your system meets the requirements in the [compatibility guide](compatibility.md)
3. Run the `quick_test.sh` script to perform a comprehensive system check
4. For AppImage-specific issues, try running with debug logging:
   ```bash
   ADAPTIVE_EQ_LOG_LEVEL=debug ./Adaptive_EQ-x86_64.AppImage
   ```

## Contributing

Contributions to documentation are welcome! Please feel free to submit pull requests to improve or expand the documentation.
