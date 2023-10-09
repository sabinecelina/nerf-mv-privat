import React, { useState, useRef } from 'react';
import { Carousel } from 'react-bootstrap';

const VideoSlider = () => {
  const videoContext = require.context('./videos', false, /\.mp4$/);

  const videos = videoContext.keys().map(videoContext);

  const [currentIndex, setCurrentIndex] = useState(0);
  const videoRef = useRef(null);

  const handleSlideChange = newIndex => {
    setCurrentIndex(newIndex);
    videoRef.current.load();
  };

  return (
    <div className="slider">
      {videos.length > 0 && (
        <Carousel activeIndex={currentIndex} onSelect={handleSlideChange}>
          {videos.map((video, index) => (
            <Carousel.Item key={index}>
              <video
                ref={videoRef}
                autoPlay
                muted
                className="d-block w-100"
                style={{ outline: 'none', maxWidth: '100%', maxHeight: '50vh' }}
              >
                <source src={video} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </Carousel.Item>
          ))}
        </Carousel>
      )}
    </div>
  );
};

export default VideoSlider;
