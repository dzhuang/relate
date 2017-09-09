#! /bin/bash

# before_script
if [[ $Flake8 == true ]]; then
  curl -L -O -k https://gitlab.tiker.net/inducer/ci-support/raw/master/prepare-and-run-flake8.sh
fi

if [[ $Mypy == true ]]; then
  curl -L -O -k https://gitlab.tiker.net/inducer/ci-support/raw/master/prepare-and-run-mypy.sh
  cp local_settings.example.py local_settings.py
fi

if [[ $PY == true ]]; then
  # We are not using tls verify, skipping the cert bother. To disable tls verify,
  # DOCKER_TLS_VERIFY should be an empty string (0 or false won't work).
  # Ref https://github.com/moby/moby/issues/22339
  export DOCKER_TLS_VERIFY=

  # Controller for real docker unittest
  export ENABLE_DOCKER_TEST=True
  docker pull inducer/relate-runpy-i386

  # Todo: Using tls verify? Need to work round the following issue:
  # unable to configure the Docker daemon with file /etc/docker/daemon.json:
  # the following directives are specified both as a flag and in the configuration file:
  # hosts: (from flag: [unix:///var/run/docker.sock 0.0.0.0:2376], from file: [tcp://0.0.0.0:2376 unix:///var/run/docker.sock]),
  # ip-forward: (from flag: false, from file: false),
  # tlscert: (from flag: /home/travis/.docker/server-cert.pem, from file: /home/.docker/server-cert.pem),
  # tlskey: (from flag: /home/travis/.docker/server-key.pem, from file: /home/.docker/server-key.pem)
fi

# run ci according to env variables
if [[ $PY == true ]]; then
  . ./run-tests-for-ci.sh
elif [[ $Mypy == true ]]; then
  . ./prepare-and-run-mypy.sh python3.6 mypy==0.521 typed-ast==1.0.4
elif [[ $Flake8 == true ]]; then
  . ./prepare-and-run-flake8.sh relate course accounts test bin
fi
