#!/bin/bash

IMAGE_VERSION="1.0"
docker build -t dimpon/mysql-controller:$IMAGE_VERSION .
docker push dimpon/mysql-controller:$IMAGE_VERSION