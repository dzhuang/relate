#!/usr/bin/env bash

# this script needs to be added to crontab
# 0 5 1 * * /home/course/relate/ssl.sh
systemctl stop nginx
docker  exec  acme.sh --issue -d www.learningwhat.com  --standalone --force
systemctl start nginx
nginx -s reload
