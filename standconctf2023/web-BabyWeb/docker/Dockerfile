FROM busybox:latest

COPY baby_web flag.txt /

RUN adduser -D baby_web \
    && chmod 755 baby_web flag.txt \
    && chmod u+s /bin/ping

USER baby_web

EXPOSE 63703
CMD ["/baby_web", "-a", ":63703"]