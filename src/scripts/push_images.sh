#!/bin/sh

# authenticate to artifact registry
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://europe-west1-docker.pkg.dev

# tag images
docker tag outbound europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/outbound
docker tag data_delivery europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/data_delivery
docker tag data_analysis europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/data_analysis
docker tag administrator_analysis europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/administrator_analysis
docker tag logging europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/logging

# push images
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/outbound
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/data_delivery
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/data_analysis
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/administrator_analysis
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/logging