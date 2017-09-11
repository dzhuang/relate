FROM inducer/relate-runpy-i386
MAINTAINER Andreas Kloeckner <inform@tiker.net>
EXPOSE 9941
RUN useradd runpy

RUN apt-get update
RUN apt-get -y -o APT::Install-Recommends=0 -o APT::Install-Suggests=0 install glpk-utils python3-pulp python3-jinja2 python3-networkx
RUN fc-cache