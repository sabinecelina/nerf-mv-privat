#!/bin/bash

docker run --gpus all \
  -v ./video:/nerf-industrial-metaverse/nerf_industrial_metaverse/videos \
  --rm -it \
  nerf_mv