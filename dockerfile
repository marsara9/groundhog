FROM python:3
RUN apt-get update
RUN apt-get install -y iproute2 iw wireguard
#RUN apt-get install -y iproute2 network-manager wireguard strace sudo
#RUN systemctl mask NetworkManager.service

#RUN dbus-uuidgen > /var/lib/dbus/marchine-id
#RUN mkdir /var/run/dbus
#RUN dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address > dbus_path
#RUN export DBUS_SYSTEM_BUS_ADDRESS=$(cat dbus_path)
#ENV DBUS_SYSTEM_BUS_ADDRESS="$(cat dbus_path)"
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

WORKDIR /server
RUN bash -c 'mkdir -p database/{users,config}'
COPY ui ./ui
COPY vpnserver.py .
RUN useradd -m dockeruser
RUN chown -R dockeruser /server
USER dockeruser
RUN pip3 install simplejson bcrypt nmcli
EXPOSE 8080
ENTRYPOINT ["python3", "-u", "vpnserver.py"]
