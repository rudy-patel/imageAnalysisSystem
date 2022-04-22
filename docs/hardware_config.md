### Hardware Configuration
Hardware Configuration from new (note that these instructions are from April 20th, 2022 and will be subject to change)

1)  Get a blank SD card and download Raspberry Pi OS (32-bit) onto it. Used the official Raspberry Pi Imager, which can be found and downloaded [here](https://www.raspberrypi.com/news/raspberry-pi-imager-imaging-utility/)
2)  Insert the SD card into the Pi and follow the initial set up instructions to set the language, keyboard, and timezone.
3)  Set a username and password: currently `lfias-capstone` and `p@ssworD`
4)  Connect to a network (either during setup or afterwards using the OS)
5)  Either automatically update software packages or run the following commands in the terminal after initial setup:
  *  `sudo apt-get update`
  *  `sudo apt-get upgrade`
  *  `sudo rpi-update`
6)  Activate the camera (liable to change in future Pi firmware versions)
  * `sudo raspi-config`
  * Select: Interface Options > Activate Legacy Camera Support
8)  Update the Hostname (visible name of the device on the network): currently lfiaspi
  * `sudo raspi-config`
  * Select: System Options > Hostname