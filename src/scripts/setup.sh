#!/bin/sh

# copy interceptor to microservices
cp runtime_interceptor/runtime_interceptor.py microservices/data_delivery/runtime_interceptor.py
cp runtime_interceptor/runtime_interceptor.py microservices/data_analysis/runtime_interceptor.py

# build docker containers
docker build -f microservices/logging/Dockerfile . -t logging
docker build -f outbound/Dockerfile . -t outbound
docker build -f microservices/data_delivery/Dockerfile . -t data_delivery
docker build -f microservices/data_analysis/Dockerfile . -t data_analysis
docker build -f microservices/administrator_analysis/Dockerfile . -t administrator_analysis