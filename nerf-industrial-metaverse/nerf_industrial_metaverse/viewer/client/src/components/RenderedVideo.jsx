import React, { useEffect, useState } from 'react';
import ReactPlayer from 'react-player';
import { socket } from './socket'
import ImageSlider from './ImageSlider';
const RenderedVideo = () => {

  const [videoSource, setVideoSource] = useState('');
  const [videoRenderingDone, setVideoRenderingDone] = useState(false);
  const [trainedFileURL, setTrainedFileURL] = useState('');
  const [trainedFileName, setTrainedFileName] = useState('');
  const [trainingDone, setTrainingDone] = useState(false);

  useEffect(() => {
    socket.on('training_complete', () => {
      setTrainingDone(true);
      fetchTrainingUrl();
      fetchFilename();
    });
    socket.on('rendering_complete', () => {
      setVideoRenderingDone(true);
      fetchVideoUrl();
    });
  }, []);

  const fetchVideoUrl = () => {
    fetch('/api/rendered-video-url')
      .then((response) => response.blob())
      .then((blob) => {
        const videoURL = URL.createObjectURL(blob);
        setVideoSource(videoURL);
      });
  };

  const fetchTrainingUrl = () => {
    fetch('/api/trained-file-url')
      .then((response) => response.blob())
      .then((blob) => {
        const trainedFileURL = URL.createObjectURL(blob);
        setTrainedFileURL(trainedFileURL);
      });
  };

  const fetchFilename = () => {
    fetch('/get-filename')
      .then((response) => response.json())
      .then((data) => {
        const { filename } = data;
        setTrainedFileName(filename);
        console.log(trainedFileName)
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = trainedFileURL;
    link.download = trainedFileName;
    link.click();
  };
  const handleVideo = () => {
    // Send a request to Flask to start rendering the video
    fetch('/render-video')
      .then(response => {
        // Handle the response as needed
        console.log('Video rendering started');
      })
      .catch(error => {
        // Handle errors
        console.error('Error rendering video:', error);
      });
  };

  return (
    <>
      {trainingDone && (
        <div>
          <header className="container">
            <h2>Output Screenshots from Trained NeRF</h2>
          </header>
          <ImageSlider />
          <div className="container my-3">
            {videoRenderingDone &&
              <div className="video-container">
                <ReactPlayer
                  url={videoSource}
                  controls={true}
                  playing={true}
                  width="100%"
                  height="100%"
                  className="react-player"
                />
              </div>}
            <button className="download-button-container btn btn-primary my-3" onClick={handleDownload}>
              Download Training
            </button>
            {!videoRenderingDone &&
              <button className="video-button-container btn btn-primary m-3" onClick={handleVideo}>
                Render Video
              </button>
            }
          </div>
        </div>
      )}
    </>
  );
};

export default RenderedVideo;
