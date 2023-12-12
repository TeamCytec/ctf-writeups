FROM scratch

COPY baby_binary flag.txt ynetd-static /

EXPOSE 64852
ENTRYPOINT ["/ynetd-static", "-sh", "n", "-p", "64852", "/baby_binary"]
