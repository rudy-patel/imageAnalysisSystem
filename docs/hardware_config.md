### Hardware Configuration

Two **Raspberry Pi 4**'s were used and configured using the same series of steps.

1)  Raspberry Pi OS (32-bit) was downloaded onto a freshly formatted SD card using the official Raspberry Pi Imager.
2)  The SD card was inserted and Pi was booted; set Canada location, English (Canada) language, and set Edmonton Time Zone.  Use English language and use US keyboard checkboxes were both selected.
3)  Default user passwords were changed to `lfias_capstone`
4)  Software updates were automatically run after connecting to a Wifi network.
5)  Client hostnames were set (`lfias-pi-steven` for one board and `lfias-pi-huda` for the other)
6)  The legacy Pi camera interface was enabled (`sudo raspi-config` was run in the terminal to select this option)

After restarting, the boards were ready for additional installation of functionality packages and local processing libraries/models.
