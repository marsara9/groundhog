FROM python:3
RUN apt-get update
RUN apt-get install net-tools
WORKDIR /server
RUN bash -c 'mkdir -p database/{users,config}'
COPY ui ./ui
COPY vpnserver.py .
RUN useradd -m dockeruser
RUN chown -R dockeruser /server
USER dockeruser
RUN pip3 install simplejson bcrypt
EXPOSE 8080
ENTRYPOINT ["python3", "-u", "vpnserver.py"]
