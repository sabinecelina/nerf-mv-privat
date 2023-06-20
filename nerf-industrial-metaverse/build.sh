#!/bin/bash

docker buildx bake --progress=plain -f docker/docker-bake.hcl --set *.tags=nerf_gpu_mv dev