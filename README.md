# rtl-aprs-igate
Docker container for RX-only APRS Igate using RTL-SDR

Build a docker container for receiving APRS packets with an RTL-SDR and pushing the packets to the APRS-IS servers.

# Build
Build this container with `docker build -t rtl-aprs-igate .`

Currently the container doesn't work. To run this:

* Edit the dirwolf.conf file with your callsign and login information
* start container with `docker run -it --rm --network=host --device=/dev/bus/usb -v ~/rtl-aprs-igate/direwolf.conf:/root/direwolf.conf:ro rtl-aprs-igate bash`
* Inside the container, `export LD_LIBRARY_PATH="/usr/local/lib"`
* Run the rtl_fm | direwolf command: `rtl_fm -f 144.39M - | direwolf -c direwolf.conf -t 0 -r 24000 -D 1 -`

