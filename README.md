# rtl-aprs-igate
Docker container for receive-only APRS Igate using a RTL-SDR dongle.

This docker container receives [APRS](https://en.wikipedia.org/wiki/Automatic_Packet_Reporting_System) packets with an RTL-SDR dongle and sends the packets to the APRS-IS servers.

## Hardware Required
I recommend the [RTL-SDR Blog v3 or v4](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/) dongles, they are only a few dollars more than the cheap Chinese knockoffs and they work so much better.

If you have more than one RTL-SDR dongle, set each one with a unique device_index (serial number). This is an 8-character string (such as SDR00005) set on the RTL-SDR dongle's firmware. Use `rtl_eeprom` to program this (instructions below). DO NOT program a device_idx of 00000000 or 00000001 on any RTL-SDR, this causes confusion in the RTL-SDR utilities.

<details>

<summary>Programming RTL-SDR serial number</summary>

Make sure that only one RTL-SDR dongle is plugged into the computer. Jump into a new container to access the rtl_eeprom utility:
```
$ docker run -it --rm --device=/dev/bus/usb ghcr.io/bklofas/rtl-aprs-igate:latest bash
```

Then once inside the container, run rtl_eeprom:

```

root@2ca01d75885c:/# rtl_eeprom -s SDR00002
Found 1 device(s):
  0:  Generic RTL2832U OEM

Using device 0: Generic RTL2832U OEM
Found Rafael Micro R820T tuner

Current configuration:
__________________________________________
Vendor ID:		0x0bda
Product ID:		0x2838
Manufacturer:		Realtek
Product:		RTL2838UHIDIR
Serial number:		0
Serial number enabled:	yes
Bias Tee always on:	no
Remote wakeup enabled:	no
__________________________________________

New configuration:
__________________________________________
Vendor ID:		0x0bda
Product ID:		0x2838
Manufacturer:		Realtek
Product:		RTL2838UHIDIR
Serial number:		SDR00002
Serial number enabled:	yes
Bias Tee always on:	no
Remote wakeup enabled:	no
__________________________________________
Write new configuration to device [y/n]? y

Configuration successfully written.
Please replug the device for changes to take effect.
root@2ca01d75885c:/#
```

Type `exit` to quit the container, the --rm flags ensure that the container doesn't stay around after you've quit.

</details>

Ensure the RTL-SDR dongle has adequate power. If using a hub, check that it is an active externally-powered hub, not powered from the main computer. Or better yet, plug the RTL-SDR dongle directly into the host USB port, don't use a hub. Raspberry Pi's (and other small embedded computers) have a lower power limit 

You'll also need an antenna plugged into the dongle. For mobile use, any 1/4 wave mag mount works well. For home/stationary use, a J-pole or [quarter-wave ground plane antenna](https://www.klofas.com/blog/2022/quarter-wave-ground-plane-antenna/) works well.



## Run This Project
This project installs the RTL-SDR drivers and Direwolf into a docker container. No dependencies to install. Total container size is 125 to 160 MB, depending on the host architecture.

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

Reboot your computer afterwards to pick up the changes to group membership.

### 1.2 RTL DVB Kernel Module Blacklisting
The RTL DVB kernel modules must first be blacklisted on the Docker host (the computer where the RTL-SDR dongle is plugged into). Otherwise your computer will think you want to watch TV with your dongle! RTL-SDR itself is not required on the Docker host. This can be accomplished using the following commands:

```
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
sudo modprobe -r dvb_usb_rtl28xxu
```

If the `modprobe -r` command errors, reboot the computer to unload the module.

### 1.3 Configuration file

The `station.conf` file has all of the options for the RTL-SDR dongle and Direwolf.

```
mkdir -p ~/rtl-aprs-igate
curl -o ~/rtl-aprs-igate/station.conf https://raw.githubusercontent.com/bklofas/rtl-aprs-igate/master/station.conf
vim ~/rtl-aprs-igate/station.conf
```

Change your local APRS frequency, RTL-SDR device index, callsign, IGate server, etc.


### 1.4 Run The Container
1. Just to test things out: `docker run -it --rm --device=/dev/bus/usb -v ~/rtl-aprs-igate/station.conf:/station.conf:ro ghcr.io/bklofas/rtl-aprs-igate:latest`

    * This downloads a pre-built container from the Github container registry.
    * Architectures supported are i386, amd64, arm32v6, arm32v7, and arm64. Tested on amd64, arm32v7, and arm64. arm packages run on all RaspberryPi flavors. Your client will automatically download the appropriate architecture.
    * This image will start rtl_fm piping audio to direwolf, and show the received packets on STDOUT.
    * Make sure at least one RTL-SDR dongle is connected. If you have a device_idx in your station.conf file, it will use that one. Otherwise, it will pick the first available dongle to use.
    * Host networking (--network=host) is not required, since traffic is outbound only.
    * The generated `rtl_fm` command and direwolf configuration will be displayed at the beginning.
    * Startup messages and decoded packets will display in the terminal.
    * Using the --rm flag will delete the container when you kill it. Otherwise, it will stay around until you prune.
    * Ctrl-C to kill.
    * If something is broken, you can start the container (without running the rtl_fm command) by appending `bash` on the end of the docker run command

1. For a more permanent setup, run the container in the background: `docker run -d --name rtl-aprs-igate --restart=unless-stopped --log-driver=local --device=/dev/bus/usb -v ~/rtl-aprs-igate/station.conf:/station.conf:ro ghcr.io/bklofas/rtl-aprs-igate:latest`

    * -d: Start this container in daemon/background mode.
    * --name: Name this anything you want.
    * --restart=unless-stopped: Automatically restart the container if something happens (reboot, USB problem), unless you have manually stopped the container.
    * --log-driver=local: By default, docker uses the json log driver which may fill up your harddrive, depending on how busy your station is. local log driver defaults to 100MB of saved logs, and automatically rotates them.
    * --device=: Allows the container to talk to the USB bus to access the RTL-SDR dongle.
    * -v: Mounts the config files inside the container.
    * View the last 25 log lines with `docker logs -n 25 --follow rtl-aprs-igate`
    * Stop the container with `docker stop rtl-aprs-igate`
    * Use `docker restart rtl-aprs-igate` to reload the station.conf configuration file.

## Jump Into the Container

If you just want to start a new container but not actually start rtl_fm and direwolf (such as for running the rtl_eeprom utility):

```
docker run -it --rm --device=/dev/bus/usb -v ~/rtl-aprs-igate/station.conf:/station.conf:ro ghcr.io/bklofas/rtl-aprs-igate:latest bash
```

If you're already running this container in background/daemon mode, you can jump into the running container with `docker exec -it rtl-aprs-igate bash`

Once you're inside the container, you can run any of the RTL-SDR utilities manually such as `rtl_eeprom` or `rtl_test`, or `python3 ./run.sh` to run the script, or `direwolf` and options to run direwolf.


## Build Container Locally
To build this container locally, check out this repository and build with `docker build -t rtl-aprs-igate .` Image size will be between 140 and 170 MB depending on your computer architecture.

Alternatively you can build the container with `docker build -t rtl-aprs-igate https://github.com/bklofas/rtl-aprs-igate.git`

If you'd like to build the container against a branch `docker build -t rtl-aprs-igate-branch https://github.com/bklofas/rtl-aprs-igate.git#branch_name`


## Future Work

* Use TBEACON in direwolf, which requires GPSD input
* Add docker compose file

## Versions

1. Version 1.0:
    * ghcr.io/bklofas/rtl-aprs-igate:v1.0
    * Original release, no RTL-SDR options available
1. Version 2.0:
    * ghcr.io/bklofas/rtl-aprs-igate:v2.0
    * Added station.conf configuration file for RTL-SDR options.
1. Version 3.0:
    * ghcr.io/bklofas/rtl-aprs-igate:v3.0
    * Generate the direwolf.conf file automatically
    * Added direwolf section to configuration file

## Acknowledgments/Inspiration

* [beardymcbeards](https://github.com/beardymcbeards) for help on the docker build container setup.
* [darksidelemm](https://github.com/darksidelemm) for the [radiosonde_auto_rx](https://github.com/projecthorus/radiosonde_auto_rx/wiki) project, where I stole a bunch of docker ideas and documentation.
* [johnboiles](https://github.com/johnboiles) and his [pi-rtlsdr-igate-docker](https://github.com/johnboiles/pi-rtlsdr-igate-docker) project, which has almost everything I wanted but uses environment variables instead of a config file.



