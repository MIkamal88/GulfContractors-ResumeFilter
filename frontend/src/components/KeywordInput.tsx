import React, { useState } from 'react';
import type { KeyboardEvent } from 'react';

interface KeywordInputProps {
  keywords: string[];
  onKeywordsChange: (keywords: string[]) => void;
}

const KeywordInput: React.FC<KeywordInputProps> = ({ keywords, onKeywordsChange }) => {
  const [inputValue, setInputValue] = useState('');

  const addKeywords = (input: string) => {
    // Split by comma and filter out empty strings
    const newKeywords = input
      .split(',')
      .map(k => k.trim())
      .filter(k => k.length > 0 && !keywords.includes(k));
    
    if (newKeywords.length > 0) {
      onKeywordsChange([...keywords, ...newKeywords]);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      addKeywords(inputValue);
      setInputValue('');
    } else if (e.key === 'Backspace' && !inputValue && keywords.length > 0) {
      onKeywordsChange(keywords.slice(0, -1));
    }
  };

  const handleInputChange = (value: string) => {
    // Check if a comma was typed
    if (value.includes(',')) {
      // Extract all complete keywords (before the last comma)
      const parts = value.split(',');
      const completeKeywords = parts.slice(0, -1).join(',');
      const remainingInput = parts[parts.length - 1];
      
      if (completeKeywords.trim()) {
        addKeywords(completeKeywords);
      }
      
      setInputValue(remainingInput);
    } else {
      setInputValue(value);
    }
  };

  const handleRemoveKeyword = (index: number) => {
    onKeywordsChange(keywords.filter((_, i) => i !== index));
  };

  return (
    <div className="keyword-input-container">
      <label className="keyword-label">Keywords</label>
      <div className="keyword-input-wrapper">
        <div className="keywords-list">
          {keywords.map((keyword, index) => (
            <span key={index} className="keyword-tag">
              {keyword}
              <button
                className="keyword-remove"
                onClick={() => handleRemoveKeyword(index)}
                type="button"
              >
                ✕
              </button>
            </span>
          ))}
        </div>
        <input
          type="text"
          className="keyword-input"
          placeholder={keywords.length === 0 ? 'Type keywords (separate with comma or Enter)...' : 'Add more...'}
          value={inputValue}
          onChange={(e) => handleInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
        />
      </div>
      <p className="keyword-hint">
        Press Enter or use commas to add keywords. Press Backspace to remove the last keyword.
      </p>
    </div>
  );
};

export default KeywordInput;
