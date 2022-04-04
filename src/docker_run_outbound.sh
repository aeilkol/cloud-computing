#!/bin/sh

# docker build -f outbound/Dockerfile . -t outbound

docker run --env-file outbound/.env --network="host" outbound
