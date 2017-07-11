# pi-topPULSE

![Image of pi-topPULSE addon board](https://static.pi-top.com/images/pulse-small.png "Image of pi-topPULSE addon board")

The pi-topPULSE accessory is available to purchase from the [pi-top website](https://pi-top.com/products/accessories).

## Table of Contents
* [Quick Start](#quick-start)
* [Hardware Overview](#hardware)
* [Software](#software)
    * [pi-topPULSE on pi-topOS](#software-pt-os)
    * [pi-topPULSE on Raspbian](#software-raspbian)
    * [How it works - 'under the hood'](#software-how-it-works)
* [Using pi-topPULSE](#using)
	* [Amazon's Alexa Voice Service](#using-avs)
	* [Using a custom Python script](#using-script)
* [Documentation & Support](#support)
	* [Links](#support-links)
	* [Troubleshooting](#support-troubleshooting)

## Quick Start <a name="quick-start"></a>
### pi-topOS
* Boot into pi-topOS (released on or after 13-07-2017)
* Plug in pi-topPULSE
* Follow on-screen instructions, if necessary
* Enjoy!

### Raspbian
* Run the following commands in the terminal (with an internet connection):

```
sudo apt-get update
sudo apt-get install pt-pulse
```

* Plug in pi-topPULSE
* Follow on-screen instructions, if necessary
* Enjoy!

## Hardware Overview <a name="hardware"></a>

pi-topPULSE is a 7x7 LED array, a speaker and a microphone. Additionally the device features ambient lights which reflect the state of the LED array, 4 around the speaker, and 3 on the underside. pi-topPULSE uses a variety of interfaces to communicate with the Raspberry Pi: the speaker uses I2S, and the LEDs and microphone use serial (UART) - Tx and Rx respectively. pi-topPULSE can be used either as a HAT or as pi-top addon.

[![Image of pi-topPULSE pin layout](https://static.pi-top.com/images/pulse-pinout.png "Jump to 'Documentation & Support' -> 'GPIO Pinout'")](#support-pinout)

## Software <a name="software"></a>
### pi-topPULSE on pi-topOS <a name="software-pt-os"></a>

All pi-topPULSE software and libraries are included and configured 'out-of-the-box' as standard on pi-topOS (released on or after 13-07-2017). Simply connect a pi-topPULSE to your pi-top, reboot if instructed to do so, and it will be automatically initialised and ready to produce light, capture and play audio. Volume control is handled by the operating system.

Download the latest version of pi-topOS at [https://pi-top.com/products/dashboard#download](https://pi-top.com/products/dashboard#download).

As mentioned in the [Hardware Overview](#hardware), the speaker on the pi-topPULSE uses I2S. This requires some configuration, which will require a reboot from a typical Raspbian configuration using the default sound drivers. This is also true in reverse - if you have configured a pi-topPULSE and you wish to use the standard HDMI or 3.5mm sound outputs, you will require a reboot.

#### Additional information
Automatic initialisation is performed by a software package called `pt-peripheral-cfg`. It contains a program called `pt-peripherals-daemon`, which runs in the background and scans for newly connected devices. If a device is detected, and the appropriate library is installed, it will be initialised.

The `pt-pulse` package on pi-topOS installs and starts this background process, as well as the Python library. In the case of pi-topPULSE, it enables I2S and configures UART for next boot, if not currently enabled/configured, and notifies the user if a reboot is required. If a reboot is not required, it will initialise the device.

### pi-topPULSE on Raspbian <a name="software-raspbian"></a>
The pi-topPULSE software exists on the Raspbian software repositories. Simply run the following commands at the terminal (and then reboot):

```
sudo apt-get update
sudo apt-get install pt-pulse
```

If you prefer to manually install the packages or want to install a specific set of packages see the [Manual Configuration and Installation](https://github.com/pi-top/pi-topPULSE/wiki/Manual-Configuration-and-Installation) page on the wiki.

### How it works - 'under the hood' <a name="software-how-it-works"></a>
For more information on how to use the library files, take a look at the [initialisation section of the 'Manual Configuration and Installation'](https://github.com/pi-top/pi-topPULSE/wiki/Manual-Configuration-and-Installation#using-the-software-library-to-manually-initialise-pi-toppulse) page on the wiki.
Also check out the [examples](https://github.com/pi-top/pi-topPULSE/tree/master/examples) folder for guidance of what the library is capable of.

## Using pi-topPULSE <a name="using"></a>

### Amazon's Alexa Voice Service <a name="using-avs"></a>

See [here](https://github.com/pi-top/Alexa-Voice-Service-Integration) for more on using pi-top's Alexa Voice Service integration.

### Using a custom Python script <a name="using-script"></a>

Using the `ptpulse` Python module requires root access to function. If you are running a script, make sure that you are running it with root access. You can do this with the "sudo" command:

	sudo python3 my_cool_pulse_script.py


Alternatively, if you are running Python in `IDLE`, please make sure you start LXTerminal and run idle or idle3 with the "sudo" command, like so:

	sudo idle3

## Documentation & Support <a name="support"></a>
### Links <a name="support-links"></a>
<!--* [GPIO Pinout](https://pinout.xyz/pinout/pi_toppulse) <a name="support-pinout"></a>-->
* [Support](https://support.pi-top.com/)

### Troubleshooting <a name="support-troubleshooting"></a>
#### Why is my pi-topPULSE not working?

* Currently, **pi-topPULSE is only supported on Raspberry Pi 3**. This is due to problems setting the UART clock speed on earlier Raspberry Pi models. It might be possible to get this to work on earlier versions, but this is not currently supported.

#### I have installed pi-topPULSE software manually...
* If you are running Linux kernel version 4.9.x previous to 4.9.35, pi-topPULSE [may not be fully functional](https://github.com/raspberrypi/linux/issues/1855). In particular, this issue prevents the pi-topPULSE LEDs from working. If you are experiencing this issue, please check your kernel version by typing `uname -r` at the terminal. You can update your kernel version to the latest by running `sudo apt-get install raspberrypi-kernel`.

* If you are attempting to use Python 3, and have installed manually, you need to ensure that you have the latest version of the PySerial module. Take a look at [the script](manual-install/upgrade-python3-pyserial) in the `manual-install` directory for how to do this.

#### The red LED on the underside of my pi-topPULSE is on - what does this mean?
* This LED indicates that the sampling rate of the microphone is set to 16kHz. By default, when plugged in, you will see that this LED is switched on, and can be used as a guide to show that it has not yet been initialised. Once initialised, the default sample rate is 22050Hz (~22KHz), and this is why the red LED is switched off. *Note: [pi-top's Amazon Alexa Voice Service integration](https://github.com/pi-top/Alexa-Voice-Service-Integration) uses 16kHz, which is denoted with the red LED being on. In this context, the red LED can be considered as an indicator that the pi-topPULSE is capturing audio.*
