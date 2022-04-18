#!/bin/sh

docker run --env-file outbound/.env --network="host" outbound
