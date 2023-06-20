import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const Information = () => {

    return (
        <div>
            <div className="my-3">
                <div className="card card-body">
                    <h4>How to train your own NeRF</h4>
                    <p>
                        This application utilizes the NeRF (Neural Radiance Fields) implementation to process camera parameters provided in a transforms.json file, which follows the format compatible with the original NeRF codebase. This script can process a video file, a zip file with an "images" folder in it. Additionally, this application supports generating camera data from Record3D, based on ARKit in the r3d format.
                    </p>
                    <p>
                        During the training process, it's crucial to ensure that the dataset meets certain criteria. For instance, the dataset should have comprehensive coverage, accurate camera data without mislabeling, and should not include blurry frames (both motion blur and defocus blur are problematic). To assist with dataset preparation, there are a few tips in this document. As a general guideline, if your NeRF model doesn't show signs of convergence within approximately 20 seconds, it's unlikely to improve significantly even with extended training. Therefore, it's recommended adjusting the data to achieve clear results during the initial stages of training. For larger real-world scenes, a slight improvement in sharpness can be attained by training for a few minutes at most, as the majority of convergence occurs within the first few seconds.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Information;
