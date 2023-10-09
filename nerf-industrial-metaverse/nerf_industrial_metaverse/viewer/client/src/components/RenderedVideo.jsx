import React, { useEffect, useState } from 'react';
import ReactPlayer from 'react-player';
import { socket } from './socket'
import ImageSlider from './ImageSlider';
import ExportMesh from './ExportMesh';
const RenderedVideo = () => {

  const [videoSource, setVideoSource] = useState('');
  const [videoRenderingDone, setVideoRenderingDone] = useState(false);
  const [trainedFileURL, setTrainedFileURL] = useState('');
  const [trainedFileName, setTrainedFileName] = useState('');
  const [trainingDone, setTrainingDone] = useState(false);
  const [downloadButtonDisabled, setDownloadButtonDisabled] = useState(false);
  const [videoButtonDisabled, setVideoButtonDisabled] = useState(false);

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

  const handleDownload = () => {
    setDownloadButtonDisabled(true);

    const link = document.createElement('a');
    link.href = trainedFileURL;
    link.download = trainedFileName;
    link.click();

    setTimeout(() => {
      setDownloadButtonDisabled(false);
    }, 5000);
  };
  const handleVideo = () => {
    setVideoButtonDisabled(true);
    fetch('/render-video')
      .then(response => {
        console.log('Video rendering started');
      })
      .catch(error => {
        console.error('Error rendering video:', error);
      })
      .finally(() => {
        setTimeout(() => {
          setVideoButtonDisabled(false);
        }, 5000);
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
            <ExportMesh />
            <button
              className="download-button-container btn btn-primary my-3"
              onClick={handleDownload}
              disabled={downloadButtonDisabled}
            >
              Download Training
            </button>
            {!videoRenderingDone &&
              <button
                className="video-button-container btn btn-primary m-3"
                onClick={handleVideo}
                disabled={videoButtonDisabled}
              >
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
