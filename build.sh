#!/bin/bash

image=hub.cerit.io/josef_handl/ddiag
tag=22.04

docker build --build-arg="tag=${tag}" -t "${image}:${tag}" .
docker push "${image}:${tag}"
