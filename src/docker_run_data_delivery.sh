#!/bin/sh

# docker build -f microservices/data_delivery/Dockerfile . -t data_delivery

docker run --env-file microservices/data_delivery/.env --network="host" data_delivery
