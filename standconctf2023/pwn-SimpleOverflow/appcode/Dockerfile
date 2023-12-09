# to build:
# docker build -t challenge_bof1 .
# to run:
# docker run -d -p 1337:1337 --rm -it challenge_bof1

FROM ubuntu:20.04

RUN apt-get update && apt -qy dist-upgrade

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY bof1 .
COPY flag.txt .
COPY ynetd .
RUN chown -R root:root /home/ctf

USER ctf
EXPOSE 1337
CMD ./ynetd -p 1337 ./bof1
