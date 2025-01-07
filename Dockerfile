#LABEL org.opencontainers.image.authors="Bryan Klofas KF6ZEO bklofas@gmail"

FROM debian:bookworm-slim

LABEL "name"="rtl-aprs-igate" \
  "description"="APRS Igate using RTL-SDR dongle" \
  "author"="Bryan Klofas KF6ZEO"

RUN apt-get -y update && apt -y upgrade && apt-get -y install --no-install-recommends \
    cmake \
    build-essential \
    ca-certificates \
    git \
    libusb-1.0-0-dev \
    pkg-config \
    libasound2-dev && \
#    libhamlib4 \
#    libhamlib-utils \
#    libhamlib-dev && \
    rm -rf /var/lib/apt/lists/*

# install everything in /target and it will go in to / on destination image. symlink make it easier for builds to find files installed by this.
#RUN mkdir -p /target/usr && rm -rf /usr/local && ln -sf /target/usr /usr/local && mkdir /target/etc

RUN git clone --depth 1 https://github.com/rtlsdrblog/rtl-sdr-blog.git && \
    cd rtl-sdr-blog && \
    mkdir build && \
    cd build && \
    cmake ../ -DINSTALL_UDEV_RULES=ON && \
    make && \
    make install
#    cp ../rtl-sdr.rules /etc/udev/rules.d/ && \
#    ldconfig && \
#    echo 'blacklist dvb_usb_rtl28xxu' > /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

#COPY scripts/* /target/usr/bin/

RUN git clone --depth 1 https://github.com/wb2osz/direwolf.git && \
    cd direwolf && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j4 && \
    make install

# Use tini as init.
#ENTRYPOINT ["/usr/bin/tini", "--"]

# Run rtl_fm -> direwolf
CMD ["rtl_fm", "-f", "144.39M", "-", "|", "direwolf", "-c", "direwolf.conf", "-t", "0", "-r", "24000", "-D", "1", "-"]

