import React, { useState } from 'react';
import PropTypes from 'prop-types';

const Accordion = ({ cards }) => {
  const [activeIndex, setActiveIndex] = useState(null);

  const handleCardClick = (index) => {
    setActiveIndex((prevIndex) => (prevIndex === index ? null : index));
  };

  const renderCards = () => {
    return cards.map((card, index) => (
      <div
        key={index}
        className={`card my-2 ${activeIndex === index ? 'active' : ''}`}
      >
        <div
          className="card-header"
          onClick={() => handleCardClick(index)}
        >
          <span className={`arrow mx-2 ${activeIndex === index ? 'open' : ''}`}>&#8595;</span>
          {card.title}
        </div>
        {activeIndex === index && (
          <div className="card-body">{card.content}</div>
        )}
      </div>
    ));
  };

  return <div className="accordion">{renderCards()}</div>;
};

Accordion.propTypes = {
  cards: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string.isRequired,
      content: PropTypes.node.isRequired,
    })
  ).isRequired,
};

export default Accordion;
