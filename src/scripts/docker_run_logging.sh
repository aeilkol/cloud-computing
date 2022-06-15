#!/bin/sh

docker run --env-file microservices/logging/.env --network="host" logging
