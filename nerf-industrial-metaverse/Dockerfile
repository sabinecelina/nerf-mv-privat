FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

ARG COLMAP_VERSION=dev
ENV CERES_SOLVER_VERSION=2.0.0
ARG CUDA_ARCHITECTURES=89
ENV PATH=/usr/local/cuda/bin:$PATH


RUN apt-get update && apt-get install -y python-is-python3 libsm6 libxrender1 libfontconfig1
# Prevent stop building ubuntu at time zone selection.
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update &&  \
    apt-get install -y python3-pip
RUN pip install --upgrade --no-cache-dir pip

# Prepare and empty machine for building.
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    cmake \
    ninja-build \
    build-essential \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libflann-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libsqlite3-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libceres-dev \
    nano \
    python-is-python3 \
    ffmpeg \
    curl \
    wget \
    tmux

# Install Node.js
RUN mkdir temp && cd temp && wget https://nodejs.org/dist/v16.16.0/node-v16.16.0-linux-x64.tar.xz && \
    tar -xf node-v16.16.0-linux-x64.tar.xz --strip-components=1 -C /usr/local

ENV PATH="/usr/local/bin:${PATH}"

RUN rm -r temp
# Install Ceres-solver (required by colmap).
RUN echo "Installing Ceres Solver ver. ${CERES_SOLVER_VERSION}..." \
	&& cd opt \
	&& git clone https://github.com/ceres-solver/ceres-solver \
	&& cd ceres-solver \
	&& git checkout ${CERES_SOLVER_VERSION} \
	&& mkdir build \
	&& cd build \
	&& cmake ../ -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF \
    && make -j \
    && make install && \
    cd ../.. && \
    rm -rf ceres-solver

RUN echo "Installing COLMAP ver. ${COLMAP_VERSION}..."
RUN git clone https://github.com/colmap/colmap.git
RUN cd colmap && \
    git reset --hard ${COLMAP_VERSION} && \
    mkdir build && \
    cd build && \
    cmake .. -GNinja -DCMAKE_CUDA_ARCHITECTURES=89 && \
    ninja && \
    ninja install && \
    cd .. && rm -rf colmap

# Build instant-nerf wihout gui
RUN echo "Installing Instant-NeRF"
RUN  git clone --recursive https://github.com/nvlabs/instant-ngp
RUN cd instant-ngp && \
    cmake -DNGP_BUILD_WITH_GUI=off ./ -B ./build && \
    cmake --build build --config RelWithDebInfo -j 16

ADD . nerf-industrial-metaverse
RUN cp instant-ngp/build/pyngp.cpython* /nerf-industrial-metaverse
RUN cd nerf-industrial-metaverse && pip install -e . 
RUN cd nerf-industrial-metaverse/nerf_industrial_metaverse/viewer/client && npm install 
RUN pip install flask-cors
WORKDIR nerf-industrial-metaverse/nerf_industrial_metaverse
