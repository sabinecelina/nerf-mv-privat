import React from 'react';
import Accordion from './Accordion';
import cameramotion from '../images/camera_motion.png';
import TerminateProcess from './TerminateProcess';
const MyCard = () => {
  const cards = [
    {
      title: 'How to Capture a Quality Video?',
      content: (
        <div className="text-left">
          <p className="mb-2">
            For optimal results, it's crucial to prepare a good dataset. Below is an image illustrating beneficial and detrimental camera movements. Aim to capture the scene slowly and make sure to circle the object at least twice from two different perspectives.
          </p>
          <div className="text-center">
            <img
              src={cameramotion}
              alt="Beneficial and Detrimental Camera Movements"
              className="card-image mx-auto text-center"
              style={{ maxWidth: '50%', height: 'auto' }}
            />
          </div>
        </div>
      ),
    },
    {
      title: 'Terminate Server Processes After Reloading the Page',
      content: (
        <div>
          <p>If the page is reloaded, server processes may continue to run in the background without client communication. Use the button below to terminate these processes. Exercise caution while doing so.</p>
          <TerminateProcess />
        </div>
      ),
    }
  ];
  

  return (
    <div>
      <Accordion cards={cards} />
    </div>
  );
};

export default MyCard;