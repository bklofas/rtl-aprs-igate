# rtl-aprs-igate
Docker container for RX-only APRS Igate using a RTL-SDR dongle.

Build a docker container for receiving APRS packets with an RTL-SDR and pushing the packets to the APRS-IS servers.

# Build and Run
Build this container with `docker build -t rtl-aprs-igate .`

* Edit the direwolf.conf file with your callsign and login information.
* start container with `docker run -it --rm --network=host --device=/dev/bus/usb -v ~/rtl-aprs-igate/direwolf.conf:/root/direwolf.conf:ro rtl-aprs-igate`
* This will automatically run `rtl_fm -f 144.39M - | direwolf -c direwolf.conf -r 24000 -`

# Future Work

* Ability to add rtl_fm command-line options, such as different RX frequency, device index, gain, etc. This will require some scripting to read a config file

# Acknowledgments/Inspiration

* @beardymcbeards for help on the docker build container setup
* @johnboiles and his [pi-rtlsdr-igate-docker](https://github.com/johnboiles/pi-rtlsdr-igate-docker) project, which has almost everything I wanted but uses environment variables instead of a config file
* @darksidelemm for the [radiosonde_auto_rx](https://github.com/projecthorus/radiosonde_auto_rx/wiki) project, where I stole a bunch of docker ideas


