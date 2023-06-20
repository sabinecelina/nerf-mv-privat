import React, { useState, useEffect } from 'react';
import { Carousel } from 'react-bootstrap';
import { socket } from './socket';

const Slider = () => {
  const [images, setImages] = useState([]);
  const [trainingComplete, setTrainingComplete] = useState(false);
  const fetchImages = async () => {
    try {
      const response = await fetch('/api/images');
      const data = await response.json();
      setImages(data.images);
    } catch (error) {
      console.error('Error fetching images:', error);
    }
  };
  useEffect(() => {
    // Listen for the 'training_complete' event
    socket.on('training_complete', handleTrainingComplete);

    // Clean up the event listener
    return () => {
      socket.off('training_complete', handleTrainingComplete);
    };
  }, []);

  const handleTrainingComplete = () => {
    fetchImages();
    setTrainingComplete(true);
  };

  return (
    <div className="slider">
      {trainingComplete && images.length > 0 && (
        <Carousel>
          {images.map((image, index) => (
            <Carousel.Item key={index}>
              <img
                className="d-block w-100"
                src={`/api/images/${image}`}
                alt={`Slider Image ${index + 1}`}
              />
            </Carousel.Item>
          ))}
        </Carousel>
      )}
    </div>
  );
};

export default Slider;
