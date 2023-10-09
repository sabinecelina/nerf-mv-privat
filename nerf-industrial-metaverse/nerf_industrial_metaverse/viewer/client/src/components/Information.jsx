import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const Information = () => {

    return (
        <div>
            <div className="my-3">
                <div className="card card-body">
                    <h4>How to Train Your Own Neural Radiance Field?</h4>
                    <p>
                        This application utilizes the instant-ngp framework for training Neural Radiance Fields (NeRFs). For foundational understanding of the technology, you may refer to: https://neuralradiancefields.io/. The primary objective of this application is to train a neural network to represent a captured scene in 3D. Accepted input formats include videos, images in a .zip file, or R3D files generated using the iPhone app Record3D. Default parameters have been optimized to yield the best results in most scenarios. If any issues arise during the process, you may re-upload the video and click "Start Training"; the program will resume from where it left off.
                    </p>
                    <div className="alert alert-warning" role="alert">
                        Note: It is essential to keep this page open in the background to maintain the same socket client connection.
                    </div>
                    <p>
                        To achieve optimal results, consider refining the dataset. For video input, ensure the subject is captured from multiple angles and that overlapping of objects is present for feature matching across frames. For images, avoid uploading blurred pictures, and again, make sure there is object overlap. Upon completion of the pipeline, you will be able to view training screenshots and render a video. The trained model can also be downloaded and viewed in the NGP-GUI.
                    </p>
                    <h4>Additional Important Details Regarding Training:</h4>
                    <p>
                        Graphic card memory is limited; therefore, only a certain number of images will be extracted to fit within this constraint. By default, every second frame is extracted, up to a maximum of 400 images (approximately equivalent to a 30-second video). To accommodate longer videos, you can adjust the frame extraction rate using the "ChangeConfig" - Video Downsample option. For example, setting the value to 10 will extract every 10th frame, thus allowing for a longer video duration. Increasing the "Max Image of Video" configuration will only result in exceeding the GPU memory limit, rendering the training of a NeRF model unfeasible.
                    </p>
                </div>
            </div>
        </div>

    );
};

export default Information;
