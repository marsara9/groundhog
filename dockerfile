FROM python:3
RUN apt-get update
RUN apt-get install -y net-tools network-manager wireguard
RUN systemctl enable NetworkManager.service
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
