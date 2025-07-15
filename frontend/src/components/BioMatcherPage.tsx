import React from 'react';
import BioMatcherUpload from './BioMatcherUpload';
import './BioMatcherPage.css';

const BioMatcherPage: React.FC = () => {
  return (
    <div className="bio-matcher-page">
      <div className="page-header">
        <h1>Bio-Matcher</h1>
        <p>Upload and merge biological data files automatically</p>
      </div>
      
      <BioMatcherUpload />
    </div>
  );
};

export default BioMatcherPage; 