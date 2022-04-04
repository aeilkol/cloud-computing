#!/bin/sh

# docker build -f microservices/data_analysis/Dockerfile . -t data_analysis

docker run --env-file microservices/data_analysis/.env --network="host" data_analysis
