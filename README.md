# rtl-aprs-igate
Docker container for receive-only APRS Igate using a RTL-SDR dongle.

This docker container receives [APRS](https://en.wikipedia.org/wiki/Automatic_Packet_Reporting_System) packets with an RTL-SDR dongle and sends the packets to the APRS-IS servers.

## Hardware Required
I recommend the [RTL-SDR Blog v3 or v4](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/) dongles, they are only a few dollars more than the cheap Chinese knockoffs and they work so much better.

If you have more than one RTL-SDR dongle, set each one with a unique device_index (serial number). Use This is an 8-digit number (00000000 or 00000001) set on the RTL-SDR dongle's firmware. Use `rtl_eeprom` to program this (instructions below).

Ensure the RTL-SDR dongle has adequite power. If using a hub, check that it is powered

You'll also need an antenna plugged into the dongle. For mobile use, any 1/4 wave mag mount works well. For home/stationary use, a J-pole or [quarter-wave ground plane antenna](https://www.klofas.com/blog/2022/quarter-wave-ground-plane-antenna/) works well.



## Run this container
This project installs the RTL-SDR drivers and Direwolf into a docker container. No dependencies to install. Total container size is 100 to 125 MB, depending on the host architecture.

### 1.1 Install Docker
Check to see if docker is already installed by running `docker ps`. If this errors out, install Docker by using the convenience script:

```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

After docker installation, to be able to run docker commands as your non-root user (recommended!!), run:

```
sudo usermod -aG docker $(whoami)
```

You will need to logout and log back in (or reboot) afterwards to pick up the changes to group membership.

### 1.2 RTL-SDR Kernel Blacklisting
The RTL DVB kernel modules must first be blacklisted on the Docker host (the computer where the RTL-SDR dongle is plugged into). RTL-SDR itself is not required on the Docker host. This can be accomplished using the following commands:

```
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
sudo modprobe -r dvb_usb_rtl28xxu
```

If the `modprobe -r` command errors, reboot the computer to unload the module.

### 1.3 RTL Options

The `station.conf` file has all of the options for the RTL-SDR dongle.

```
mkdir -p ~/rtl-aprs-igate
curl -o ~/rtl-aprs-igate/station.conf https://raw.githubusercontent.com/bklofas/rtl-aprs-igate/master/station.conf
vim ~/rtl-aprs-igate/station.conf
```

Change your local APRS frequency, RTL-SDR device index, etc.

### 1.4 Direwolf Configuration
[Direwolf](https://github.com/wb2osz/direwolf) requires configuration before it will run correctly. Download the Direwolf configuration file and edit it locally:

```
mkdir -p ~/rtl-aprs-igate
curl -o ~/rtl-aprs-igate/direwolf.conf https://raw.githubusercontent.com/bklofas/rtl-aprs-igate/master/direwolf.conf
vim ~/rtl-aprs-igate/direwolf.conf
```

Change these options in the `direwolf.conf` file:

* MYCALL: Your personal callsign
* IGSERVER: Your local APRS-IS server, based on continent
* IGLOGIN: Your callsign and [password](https://apps.magicbug.co.uk/passcode/)
* If you want to "beacon" your receiver location to the APRS network over the internet, uncomment the PBEACON option and add your latitude/longitude

### 1.5 Run The Container
1. Just to test things out: `docker run -it --rm --device=/dev/bus/usb -v ~/rtl-aprs-igate/station.conf:/station.conf:ro -v ~/rtl-aprs-igate/direwolf.conf:/root/direwolf.conf:ro ghcr.io/bklofas/rtl-aprs-igate:latest`

    * This downloads a pre-built container from the Github container registry.
    * Architectures supported are i386, amd64, arm32v6, arm32v7, and arm64. Tested on amd64, arm32v7, and arm64. arm packages run on all RaspberryPi flavors. Your client will automatically download the appropriate architecture.
    * This image will start rtl_fm piping audio to direwolf, and show the received packets on STDOUT.
    * Make sure at least one RTL-SDR dongle is connected. If you have a device_idx in your station.conf file, it will use that one. Otherwise, it will pick the first available dongle to use.
    * Host networking (--network=host) is not required, since traffic is outbound only.
    * The generated `rtl_fm` command will be displayed at the beginning.
    * Startup messages and decoded packets will display in the terminal.
    * Using the --rm flag will delete the container when you kill it. Otherwise, it will stay around until you prune.
    * Ctrl-C to kill.
    * If something is broken, you can start the container (without running the rtl_fm command) by appending `bash` on the end of the docker run command

1. For a more permanent setup, run the container in the background: `docker run -d --name rtl-aprs-igate --restart=unless-stopped --log-driver=local --device=/dev/bus/usb -v ~/rtl-aprs-igate/direwolf.conf:/root/direwolf.conf:ro ghcr.io/bklofas/rtl-aprs-igate:latest`

    * -d: Start this container in daemon/background mode.
    * --name: Name this anything you want.
    * --restart=unless-stopped: Automatically restart the container if something happens (reboot, USB problem), unless you have manually stopped the container.
    * --log-driver=local: By default, docker uses the json log driver which may fill up your harddrive, depending on how busy your station is. local log driver defaults to 100MB of saved logs, and automatically rotates them.
    * --device=: Allows the container to talk to the USB bus to access the RTL-SDR dongle.
    * -v: Mounts the direwolf config file inside the container.
    * View the last 25 log lines with `docker logs -n 25 --follow rtl-aprs-igate`
    * Stop the container with `docker stop rtl-aprs-igate`
    * Use `docker restart rtl-aprs-igate` to reload the Direwolf configuration file.

## Jump Into the Container

docker run -it --rm --device=/dev/bus/usb -v ~/rtl-aprs-igate/station.conf:/station.conf:ro -v ~/rtl-aprs-igate/direwolf.conf:/root/direwolf.conf:ro ghcr.io/bklofas/rtl-aprs-igate bash

## Build Container Locally
To build this container locally, check out this repository and build with `docker build -t rtl-aprs-igate .` Image size will be between 140 and 170 MB depending on your computer architecture.


## Future Work

* Ability to add rtl_fm command-line options, such as different RX frequency, device index, gain, etc. This will require some scripting to read a config file
* Use TBEACON in direwolf, which requires GPSD input
* Add docker compose file

## Acknowledgments/Inspiration

* [beardymcbeards](https://github.com/beardymcbeards) for help on the docker build container setup
* [darksidelemm](https://github.com/darksidelemm) for the [radiosonde_auto_rx](https://github.com/projecthorus/radiosonde_auto_rx/wiki) project, where I stole a bunch of docker ideas and documentation
* [johnboiles](https://github.com/johnboiles) and his [pi-rtlsdr-igate-docker](https://github.com/johnboiles/pi-rtlsdr-igate-docker) project, which has almost everything I wanted but uses environment variables instead of a config file



