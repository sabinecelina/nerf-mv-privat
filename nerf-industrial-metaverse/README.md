### Generate Nerfs for Industrial Metaverse

## About this project

This project focuses on creating nerfs for the context of the industrial metaverse. It involves extracting images from videos and using colmap to obtain camera calibration information. The extracted images and poses are then used to train the NeRF (Neural Radiance Fields) model.

## Requirements

To run this project, you need the following:

- Host machine with at least one NVIDIA GPU
- Docker (for Cuda support 19.03+)

## Quick Start
1. Check Docker Version
```
docker --version
```
2. Check if Nvidia Driver is installed on your Docker machine
```
    nvidia-smi
```
You should now get an information looking like this: 
```
Thu May 25 06:46:15 2023       
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 525.105.17   Driver Version: 525.105.17   CUDA Version: 12.0     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA TITAN RTX    Off  | 00000000:1B:00.0 Off |                  N/A |
| 41%   33C    P8    16W / 280W |      0MiB / 24576MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   1  NVIDIA GeForce ...  Off  | 00000000:B2:00.0 Off |                  Off |
|  0%   38C    P8    36W / 450W |      0MiB / 24564MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
```
3. Check if the nvidia-toolkit is installed with: 
```
docker run --rm -it --gpus all nvidia/cuda:11.8.0-devel-ubuntu22.04 nvidia-smi
```
If the output is the same as above it's already installed. 

3. If not, setup the nvidia-toolkit on your host machine:

  For Ubuntu host machines: `sh setup-ubuntu.sh`

4. Load Video File

Place your video file in the nerf_industrial_metaverse folder within the development container.

5. Adjust Configuration File

Open the default.yaml file located in the configs folder.
Update the file path and name in the configuration file to match your video.
Define your project name in the configuration file.
```
name: your_project_name

dir:
    data_dir: 'data'      # It is the main dataset address containing all dataset

overwrite: True
data:
    video_path: 'video_name.mp4' # located in nerf_industrial_metaverse
    scene_name: your_project_name

```
Read comments if you want to change more in the config file. There is also a config for iphone files: 
By adding the lines 
```
iphone: 
    rotate: False
    subsample: 1
```
to the yaml file, the r3d files will be used.


4. Execute the following command to start the training process:
```
ngp-trainvideo --configs config/default.yaml
```

### Built with

Python: 3.9 <br>
Poetry: 1.4.0 <br>
Cuda: 11.7 <br>

### This script is inspired from

https://github.com/NVlabs/instant-ngp/tree/master/scripts
https://github.com/TencentARC/ArcNerf

### Troubleshooting

If you get an error like this: 
```
docker: Error response from daemon: Failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error running hook #0: error running hook: exit status 1, stdout: , stderr: Mode auto-detected as 'legacy
nvidia-container-cli: Initialisation error: WSL environment detected but no adapters found: unknown.
```
Please try the following command and reboot your computer.
```
wsl --upgrade
```

If you get something like this: 
```
command not found \r
```

install dos2unix in your wsl, and convert the setup-ubuntu.sh file to your system configuration
```
dos2unix setup-ubuntu.sh
```

### Author

Sabine Schleise
sabine.schleise@sick.de

### Citation

https://colmap.github.io/install.html

Schönberger, J.L. and Frahm, J.-M. (2016). Structure-from-Motion Revisited. In Conference on Computer Vision and Pattern
Recognition (CVPR).

Schönberger, J.L., Zheng, E., Pollefeys, M. and Frahm, J.-M. (2016). Pixelwise View Selection for Unstructured
Multi-View Stereo. In European Conference on Computer Vision (ECCV).

Müller, T., Evans, A., Schied, C. and Keller, A. (2022). Instant Neural Graphics Primitives with a Multiresolution Hash
Encoding. ACM Trans. Graph., 41(4), 102:1-102:15. doi: 10.1145/3528223.3530127.
