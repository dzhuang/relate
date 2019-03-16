#!/usr/bin/env bash

# this script needs to be added to crontab
# 0 5 1 * * /home/course/relate/ssl.sh
docker rm /acme.sh --force
docker run --rm  -itd    -v "/etc/nginx/cert":/acme.sh    --net=host   --entrypoint /bin/sh   --name=acme.sh   neilpang/acme.sh
systemctl stop nginx
docker  exec  acme.sh --issue -d www.learningwhat.com  --standalone
systemctl start nginx
nginx -s reload
