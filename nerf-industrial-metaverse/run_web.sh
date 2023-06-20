#!/bin/bash

# Start React app
cd nerf_industrial_metaverse/viewer/client
npm start &

# Start Flask app
cd ../server
flask run &