# Groundhog - Router

![docker build](https://github.com/marsara9/groundhog/actions/workflows/docker-build.yml/badge.svg)


## About

A simple router and web interface that's centered around maintaining an VPN connection.

The idea is to install this on any device that has at least two interfaces.  Either two ethernet ports or one eithernet and one WiFi.  One interface will always be used to connect to an existing network and all others will be used to create a separate network that is always connected to the VPN.

The system will attempt to auto-configure itself as much as possible but a web interface is exposed on port `8080` that can be accessed to configure the router, including the VPN settings.

Upon first launching the router a default user `admin` with the password `admin` will be created.  It's advised that you change this user's password or even create a new user and delete the original admin account as soon as possible.

All configurations and settings are stored in a `database/`.  Most of the files inside `database/config` are system specific though, and shouldn't be transferred or copied.

Users are stored in `database/users`.  Users can be modified via the web interface, but you can edit details in the raw files as well.  Should you accidently delete all users though, you won't be able to log into web interface.  Restarting the router though will re-create the default admin account as explained abbove.

Lastly, the software here currently only support Wireguard for a VPN.  Other protocols may be added in the future, but due to hardware constraints and limitations on my end, I currently only support Wireguard.

## Installation

Preferred installation is via docker, ideally docker compose.  Default images are provided for [docker](https://hub.docker.com/r/marsara9/groundhog/tags).  

Example `docker-compose.yml`:
```yaml
version: '3.5'
services:
  groundhog:
    image: marsara9/groundhog:latest
    container_name: groundhog
    cap_add:
      - NET_ADMIN
    security_opt:
      - apparmor:unconfined
    environment:
      - TZ=America/New_York
    ports:
      - 8080:8080 # default web interface port
      - 67:67/udp # DHCP 
    volumes:
      - /var/run/dbus:/var/run/dbus
      - /docker/groundhog/database:/router/database
    restart: unless-stopped
```

Certain options are required for this to function, mainly the `apparmor:unconfied`, as the router will be managing your host's network interfaces, even inside the container.

It's also suggested that you use a reverse-proxy, such as [ngnix](https://hub.docker.com/_/nginx) to enable HTTPS support.  A sample nginx configuration is provided [here](https://github.com/marsara9/groundhog/blob/master/docker/docker-compose.yml) and [here](https://github.com/marsara9/groundhog/blob/master/nginx/nginx.conf).

### Building and running outside of Docker.

#### Using the build script (Debian based systems only)

```
$ sudo chmod +x docker/build.sh
$ sudo docker/build.sh
```

or if you wish to create your own docker image:

```
$ sudo chmod +x docker/build.sh
$ sudo docker/build.sh docker
```

This will install all of the required dependencies.  Afterwards you can simply start the server via:

```
$ sudo python3 server/server.py
```

#### Building manually

Alternatively you can build the router yourself and run it outside of docker.  Do to so, you'll install a few dependencies, depending on your target platform.

Dependencies:
- Python 3.10+
  - [nmcli](https://pypi.org/project/nmcli/)
  - [bcrypt](https://pypi.org/project/bcrypt/)
  - [simplejson](https://pypi.org/project/simplejson/)
- Rust 3.56+ (on armv7 systems only)
  - Required for building bcrypt on armv7 systems.

After installing all of the dependencies you can start the router by simply running:

```
$ sudo python3 server/server.py
```

Since the router does modify the systems networking interfaces root access is required.  If you start the server as a non-root user, it will still start but the server will be in read-only mode.  Meaning you'll only be able to view the current configuration, but any modifications will not function.

## Configuration

There is a master config file located in `database/config/groundhog.yml`.  Normally you shouldn't need to modify this by hand but an example here is provided should you need to troubleshoot any issues that might arise.  Explanation of each property is explained below.  Should you modify any of the configurations provided here, you should reboot or otherwise restart the docker container for the router.

```yaml
mode: ethernet 
lanip: 192.168.250.1/24
dns:
  - 10.0.0.1
  - 10.0.0.5
wifi:
  ssid: "Groundhog"
  passphrase: "******"
vpn:
  endpoint: vpn.example.com:52860
  address: 10.8.0.5
  keys:
    private: --
    public: --
    preshared: --

```

| Field | Description |
| ----- | ----------- |
| mode | This MUST be either `wifi` or `ethernet`.  This specifies how the device will attempt to connect to the internet. |
| lanip | The IP address and subnet to use for any connected devices.  For example, if you set this to `192.168.250.1/24`, the device itself will have an IP address of `192.168.250.1` and any clients that connect to it via `wifi` or `ethernet` will have an IP addressed assigned to them in the range of `192.168.250.11`-`192.168.250.254`. (The first 10 addresses are reserved for any static IPs you want to assign). |
| dns | This should be set to a list of DNS servers that should be by any clients connecting to this device.  Ideally these should be set to DNS servers that are behind the VPN so that you can connect to services at the remote site. |
| wifi.ssid | When in `ethernet` mode this is the SSID that should be broadcast as a new WiFi network for clients to connect to.  When in `wifi` mode, this should be set to the SSID of the access point you want to get internet from. |
| wifi.passphrase | When in `ethernet` mode, this is the password that clients should use to connect to this device.  When in `wifi` mode this is the password that this device should use to connect to the nearby accesspoint. |
| vpn.endpoint | The IP address or URL that should be used to connect to your offsite VPN.
| vpn.address | This is the address given to you by the offsite VPN. |
| vpn.keys | These should be set to the `public`, `private` and `preshared` keys as provided by your Wireguard configuration.