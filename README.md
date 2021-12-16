# MothPi

*Mothpi* is a software for automated moth pictures used in biodiversity research.
See https://visammod.vision.in.tum.de/ for build instructions of the device.

Features:
* Timer-based capture of moth pictures
* Status updates to e-paper
* Web app for status information and configuration
* Standby during daytime based on calculated sunset and sunrise times
* Standby during bad weather, automatic weather data retrieval


## Installation

This software is programmed for use in a Rapsberry Pi with an e-paper shield and a relais shield.

### System packages

Required packages:

```bash
sudo apt-get update
sudo apt-get -y upgrade && sudo apt autoremove

sudo apt install -y python3-dev python3-pip libsystemd-dev wiringpi gphoto2
sudo pip3 install -r requirements.txt
```

### Correct time stamps

Preserve timing information as well as possible:
* Transport the camera with a battery, as it has an internal clock with limited power capacity; and check the correcttime in the camera when setting up; pictures then will have the correct timestamp.
* If the Raspberry Pi will be without internet connection, install `fake-hwclock` or optionally install a hardware clock.
* If it will have internet connection: Make sure that the systemd service `systemd-timesyncd.service` is enabled and started time zone is set correctly:

```bash
systemctl enable --now systemd-timesyncd.service
timedatectl set-ntp true 
timedatectl set-timezone "Europe/Berlin" # or any other timezone
```

### Mothpi service

Also, the Mothpi program will run as user, so make sure that [automatic start-up of user instances](https://wiki.archlinux.org/title/systemd/User#Automatic_start-up_of_systemd_user_instances) is activated:

```bash
loginctl enable-linger pi
```

### Mothpi installation

The main Mothpi programm can be downloaded from this git repository.
```bash
git clone https://github.com/lumaku/mothpi ~/mothpi
```

If you use a development version and need an access token, set up an access token in *Settings*->*Access Tokens*, then use it to access this *Mothpi* repository.

```bash
MOTHPI_TOKEN=<token>
git clone https://gitlab-ci-token:${MOTHPI_TOKEN}@gitlab.lrz.de/visammod/mothpi ~/mothpi
```

The included script automates the updating process as well as other tasks.

### Camera setup

* Switch the camera "**ON**".
* Make sure that PC connection over USB is activated. This can be verified by connecting it with USB cable to the Raspberry Pi. Then, the camera displays a "waiting for connection" message.
* To reduce power usage, switch off the display setting "Sucher" in the menu for "Display/Sucher" on Page 3 of the Gear ⚙️ page. (Sony Alpha 6000)
* Don't forget to activate the flash by pressing the flash button.


## Run Mothpi

Start with `mothpi.sh` that provides a boilerplate for mothpi, including functions for:
* automatic updates,
* systemd services,
* reverse ssh tunnel to the main server and
* a pictures uploader.

Initialize with:
```
./mothpi.sh init
```
this will copy and enable systemd services and set up systemd service variables.

The core program that takes pictures is in `mothpi/mothpy.py`.


## Mothpi App

The web app included in `mothpi/app.py` provides a web interface to check its status and change the configuration.
It can be accessed on Port 8000 by default.
The IP address of the device is displayed on the e-Paper display, if available.

Example configuration page:

![Configuration page of the Mothpi App](doc/mothpi_app_config.png)


## Mothpi default configuration


The mothpi configuration file will be saved in `$HOME/.mothpi`.
Pictures are saved in `/home/pi/pics/` and will be moved over to the server in regular intervals.

Periodic restarts are disabled by default, but can be activated over the configuration file.
