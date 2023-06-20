#!/bin/bash

# Detect Linux distribution and version
distribution=""
if [ -f "/etc/os-release" ]; then
    distribution=$(. /etc/os-release; echo "$ID$VERSION_ID")
elif [ -f "/etc/debian_version" ]; then
    distribution="debian$(cat /etc/debian_version)"
fi

if [[ $distribution == *"ubuntu"* || $distribution == *"debian"* ]]; then
    # Add the package repositories for Ubuntu/Debian
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/${distribution}/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

    # Update package repository and install nvidia-container-toolkit
    sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit

    # Configure nvidia-container-toolkit for Docker
    sudo nvidia-ctk runtime configure --runtime=docker
    # Restart Docker service
    if command -v systemctl &>/dev/null; then
        sudo systemctl restart docker
    elif command -v service &>/dev/null; then
        sudo service docker restart
    else
        echo "Failed to restart Docker service. Please restart Docker manually."
    fi

    # Check that it worked!
    echo "Checking nvidia-smi with Docker..."
    sudo docker run --rm -it --gpus all nvidia/cuda:11.7.1-devel-ubuntu22.04 nvidia-smi

else
    echo "Unsupported Linux distribution. Please install nvidia-container-toolkit manually."
fi