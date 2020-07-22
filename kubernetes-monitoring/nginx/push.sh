#!/bin/bash

IMAGE_VERSION="1.0"

docker build -t dimpon/nginx-with-metrics:$IMAGE_VERSION .
docker push dimpon/nginx-with-metrics:$IMAGE_VERSION