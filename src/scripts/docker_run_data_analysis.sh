#!/bin/sh

docker run --env-file microservices/data_analysis/.env --network="host" data_analysis
