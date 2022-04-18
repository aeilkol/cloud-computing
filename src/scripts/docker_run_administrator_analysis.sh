#!/bin/sh

docker run --env-file microservices/administrator_analysis/.env --network="host" administrator_analysis
