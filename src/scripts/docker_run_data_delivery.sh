#!/bin/sh

docker run --env-file microservices/data_delivery/.env --network="host" data_delivery
