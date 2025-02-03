# -------------------
# The build container
# -------------------
FROM debian:bookworm-slim AS build

# Upgrade bookworm and install dependencies
RUN apt-get -y update && apt -y upgrade && apt-get -y install --no-install-recommends \
    cmake \
    build-essential \
    ca-certificates \
    git \
    libusb-1.0-0-dev \
    pkg-config \
    libasound2-dev

# Build and install RTL-SDR software into /root/target/usr/local
RUN git clone --depth 1 https://github.com/rtlsdrblog/rtl-sdr-blog.git && \
    mkdir -p rtl-sdr-blog/build && \
    cd rtl-sdr-blog/build && \
    cmake ../ -DINSTALL_UDEV_RULES=ON -DCMAKE_INSTALL_PREFIX=/root/target/usr/local && \
    make && \
    make install

# Build and install Direwolf into /root/target/usr/local
RUN git clone --depth 1 https://github.com/wb2osz/direwolf.git && \
    mkdir -p direwolf/build && \
    cd direwolf/build && \
    cmake ../ -DCMAKE_INSTALL_PREFIX=/root/target/usr/local && \
    make -j4 && \
    make install


# -------------------------
# The application container
# -------------------------
FROM debian:bookworm-slim

LABEL org.opencontainers.image.title="rtl-aprs-igate"
LABEL org.opencontainers.image.description="APRS Igate using RTL-SDR dongle"
LABEL org.opencontainers.image.authors="Bryan Klofas KF6ZEO bklofas@gmail"
LABEL org.opencontainers.image.source="https://github.com/bklofas/rtl-aprs-igate"
LABEL org.opencontainers.image.licenses="MIT"

# Upgrade bookworm and install dependencies
RUN apt-get -y update && apt -y upgrade && apt-get -y install --no-install-recommends \
    tini \
    python3 \
    libusb-1.0-0-dev \
    libasound2-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy pre-built RTL-SDR and direwolf from /root/target/usr/local into /usr/local. ldconfig is for the RTL-SDR USB libraries
COPY --from=build /root/target /
RUN ldconfig

# Use tini as init.
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run python script to generate rtl_fm | direwolf command
CMD ["/bin/bash", "-c", "/run.py"]

