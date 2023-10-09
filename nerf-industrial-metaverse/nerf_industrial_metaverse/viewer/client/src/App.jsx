import React, { useState, useEffect } from 'react';
import './App.css';
import { socket } from './components/socket';
import UploadForm from './components/UploadForm';
import CheckConnection from './components/CheckConnection';
import RenderedVideo from './components/RenderedVideo';
import Information from './components/Information';
import ImageSlider from './components/ImageSlider';
import MyCard from './components/MyCard';
import VideoSlider from './components/VideoSlider';

const App = () => {
    const [isConnected, setIsConnected] = useState(socket.connected);

    useEffect(() => {
        socket.connect();

        socket.on('connect', () => {
            setIsConnected(true);
        });

        socket.on('disconnect', () => {
            setIsConnected(false);
        });

        return () => {
            socket.disconnect(); // Disconnect the socket when the component unmounts
        };
    }, []);

    return (
        <div className="container my-5">
            <h1 className="text-center mb-4">NeRF-Trainer</h1>
            <div className="row justify-content-center">
                <div className="col-lg-11">
                    <details open>
                        <summary>
                            <span class="arrow">Hide Background Information</span>
                        </summary>
                        <div className="my-2 text-center">
                            <h2>Abstract</h2>
                            <p style={{ textAlign: 'justify' }}>
                                Neural Radiance Fields (NeRF) represents a method that combines principles from classical computer graphics and machine learning to construct 3D scene representations from 2D images. Instead of directly reconstructing the complete 3D scene geometry, NeRF generates a volumetric representation known as "radiance fields," capable of assigning color and density to any point in the relevant 3D space. However, generating "neural radiance fields" requires developer expertise, substantially limiting its industrial application. Hence, we present SICK-NeRF. The NeR-Trainer is a user-friendly framework that enables the construction of custom NeRF representations, allowing anyone, regardless of their developer experience, to generate NeRFs.
                                If you haven't yet engaged with NeRF, we recommend reading the official paper: <a href="https://www.matthewtancik.com/nerf">NeRF - Representing Scenes for View Synthesis</a>.
                            </p>
                        </div>
                        <div className="my-2 text-center">
                            <h2 className="mb-3">Results from Trained NeRFs</h2>
                            <VideoSlider />
                        </div>
                        <div className="text-center">
                            <h2 className="my-3">Procedure</h2>
                            <p style={{ textAlign: 'justify' }}>
                                Creating NeRFs requires a specific approach. First, the video must be prepared to serve as training input. Individual frames from the video are extracted to later serve as training data. Using COLMAP, a Structure From Motion tool, the camera positions in the world coordinate system are estimated. These camera positions are crucial for training as the generated colors and densities heavily depend on the viewing angles.

                                COLMAP starts by extracting features from the images. These features are distinctive points that can be recognized in various images. These features must be invariant to affine transformations and brightness. COLMAP employs the SIFT algorithm here. During the feature matching step, features between pairs of images are compared to find matches.

                                Using these matches, a "Sparse Map" is created in the final step. Here, camera positions are estimated, and some points in three-dimensional space are mapped. The COLMAP step is time-consuming as images are compared pairwise, which can take a significant amount of time with many images. For further interest, we refer you to the paper: <a href="https://demuc.de/papers/schoenberger2016sfm.pdf">Structure-from_Motion Revisited</a>.

                                After the COLMAP step, the collected information is stored in a "JSON" file, which serves as input for the actual training.</p>
                        </div>
                    </details>
                    <CheckConnection isConnected={isConnected} />
                    <Information />
                    <RenderedVideo />
                    <ImageSlider />
                    <div className="card my-5">
                        <div className="card-body">
                            <UploadForm />
                        </div>
                    </div>
                    <MyCard />
                </div>
            </div>
        </div>
    );
};

export default App;
