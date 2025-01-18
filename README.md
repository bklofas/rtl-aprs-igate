# rtl-aprs-igate
Docker container for RX-only APRS Igate using a RTL-SDR dongle.

This docker container receives [APRS](https://en.wikipedia.org/wiki/Automatic_Packet_Reporting_System) packets with an RTL-SDR and sends the packets to the APRS-IS servers.

## Run this container
Run this project in a docker container. No dependencies to install. Total container size is 100 to 125 MB, depending on the host architecture.

### 1.1 Install Docker
Check to see if docker is already installed by running `docker ps`. If this errors out, install Docker by using the convenience script:

```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

To be able to run docker commands as your non-root user (recommended!!), run:

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

### 1.3 Direwolf Configuration
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

### 1.4 Run The Container
1. Just to test things out: `docker run -it --rm --network=host --device=/dev/bus/usb -v ~/rtl-aprs-igate/direwolf.conf:/root/direwolf.conf:ro ghcr.io/bklofas/rtl-aprs-igate:latest`

    * This downloads a pre-built container from the Github container registry.
    * Architectures supported are i386, amd64, arm32v6, arm32v7, and arm64. Tested on amd64, arm32v7, and arm64. arm packages run on all RaspberryPi flavors. Your client will automatically download the appropriate architecture.
    * This image will run by default `rtl_fm -f 144.39M - | direwolf -c direwolf.conf -r 24000 -`, and show the received packets on STDOUT.
    * Make sure at least one RTL-SDR dongle is connected.
    * Startup messages and decoded packets will display in the terminal.
    * Ctrl-C to kill.
    * Using the --rm flag will delete the container when you kill it. Otherwise, it will stay around until you prune.

1. For a more permanent setup, run the container in the background: `docker run -d --name rtl-aprs-igate --restart=unless-stopped --log-driver=local --network=host --device=/dev/bus/usb ghcr.io/bklofas/rtl-aprs-igate:latest`

    * -d: Start this container in daemon/background mode.
    * --name: Name this anything you want.
    * --restart=unless-stopped: Automatically restart the container if something happens (reboot, USB problem), unless you have manually stopped the container.
    * --log-driver=local: By default, docker uses the json log driver which may fill up your harddrive, depending on how busy your station is. local log driver defaults to 100MB of saved logs, and automatically rotates them.
    * --network=host: Allows the container to talk to the internet, if you are sending the packets to an online service.
    * --device=: Allows the container to talk to the USB bus to access the RTL-SDR dongle.
    * View the startup messages and decoded packets with `docker logs -n 25 --follow rtl-aprs-igate`
    * Stop the container with `docker stop rtl-aprs-igate`
    * The Direwolf configuration file gets reloaded every time you restart the container with `docker restart rtl-aprs-igate`



## Build Container Locally
To build this container locally, check out this repository and build with `docker build -t rtl-aprs-igate .` Image size will be between 100 and 125 MB depending on your computer architecture.


## Future Work

* Ability to add rtl_fm command-line options, such as different RX frequency, device index, gain, etc. This will require some scripting to read a config file
* Use TBEACON in direwolf, which requires GPSD input

## Acknowledgments/Inspiration

* [beardymcbeards](https://github.com/beardymcbeards) for help on the docker build container setup
* [darksidelemm](https://github.com/darksidelemm) for the [radiosonde_auto_rx](https://github.com/projecthorus/radiosonde_auto_rx/wiki) project, where I stole a bunch of docker ideas and documentation
* [johnboiles](https://github.com/johnboiles) and his [pi-rtlsdr-igate-docker](https://github.com/johnboiles/pi-rtlsdr-igate-docker) project, which has almost everything I wanted but uses environment variables instead of a config file



