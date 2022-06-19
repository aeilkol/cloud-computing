#!/bin/sh

# authenticate to artifact registry
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://europe-west1-docker.pkg.dev

# tag images
docker tag outbound europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/outbound:latest
docker tag data_delivery europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/data_delivery:latest
docker tag data_analysis europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/data_analysis:latest
docker tag administrator_analysis europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/administrator_analysis:latest
docker tag logging europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/logging:latest

# push images
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/outbound:latest
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/data_delivery:latest
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/data_analysis:latest
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/administrator_analysis:latest
docker push europe-west1-docker.pkg.dev/cloud-computing-347913/cloud-computing-repo/logging:latest