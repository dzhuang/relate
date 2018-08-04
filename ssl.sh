#!/usr/bin/env bash

# Note: this script need docker to be run with daemon mode

# docker run --rm  -itd  -v "/etc/nginx/cert/":/acme.sh  --net=host --name=acme.sh neilpang/acme.sh daemon

docker  exec  acme.sh --issue -d www.learningwhat.com  -w /srv/www/le_root --renew-hook "systemctl reload nginx.service"

# This script needs to be added to crontab
# 0 5 1 * * /home/course/relate/ssl.sh
