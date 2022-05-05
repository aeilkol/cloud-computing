#!/bin/sh

kubectl delete configmap outbound-config
kubectl create configmap outbound-config --from-env-file outbound/.env
kubectl delete configmap data-delivery-config
kubectl create configmap data-delivery-config --from-env-file microservices/data_delivery/.env
kubectl delete configmap data-analysis-config
kubectl create configmap data-analysis-config --from-env-file microservices/data_analysis/.env
kubectl delete configmap administrator-analysis-config
kubectl create configmap administrator-analysis-config --from-env-file microservices/administrator_analysis/.env