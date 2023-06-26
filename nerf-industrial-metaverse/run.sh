#!/bin/bash

docker run --gpus all \
   --rm -p 3000:3000 -p 5000:5000 -it \
  nerf_mv
