import React, { useState } from "react";
import type { KeyboardEvent } from "react";

interface KeywordInputProps {
  keywords: string[];
  onKeywordsChange: (keywords: string[]) => void;
  doubleWeightKeywords?: string[];
  onDoubleWeightChange?: (doubleWeightKeywords: string[]) => void;
}

const KeywordInput: React.FC<KeywordInputProps> = ({
  keywords,
  onKeywordsChange,
  doubleWeightKeywords = [],
  onDoubleWeightChange,
}) => {
  const [inputValue, setInputValue] = useState("");

  const addKeywords = (input: string) => {
    // Split by comma and filter out empty strings
    const newKeywords = input
      .split(",")
      .map((k) => k.trim().replace(/^["']|["']$/g, ""))
      .filter((k) => k.length > 0 && !keywords.includes(k));

    if (newKeywords.length > 0) {
      onKeywordsChange([...keywords, ...newKeywords]);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && inputValue.trim()) {
      e.preventDefault();
      addKeywords(inputValue);
      setInputValue("");
    } else if (e.key === "Backspace" && !inputValue && keywords.length > 0) {
      onKeywordsChange(keywords.slice(0, -1));
    }
  };

  const handleInputChange = (value: string) => {
    // Check if a comma was typed
    if (value.includes(",")) {
      // Extract all complete keywords (before the last comma)
      const parts = value.split(",");
      const completeKeywords = parts.slice(0, -1).join(",");
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
    const keywordToRemove = keywords[index];
    onKeywordsChange(keywords.filter((_, i) => i !== index));
    // Also remove from double-weight list if present
    if (onDoubleWeightChange && doubleWeightKeywords.includes(keywordToRemove)) {
      onDoubleWeightChange(doubleWeightKeywords.filter((k) => k !== keywordToRemove));
    }
  };

  const toggleDoubleWeight = (keyword: string) => {
    if (!onDoubleWeightChange) return;
    
    const isDoubleWeight = doubleWeightKeywords.includes(keyword);
    if (isDoubleWeight) {
      onDoubleWeightChange(doubleWeightKeywords.filter((k) => k !== keyword));
    } else {
      onDoubleWeightChange([...doubleWeightKeywords, keyword]);
    }
  };

  return (
    <div className="keyword-input-container">
      <label className="keyword-label">Keywords</label>
      <div className="keyword-input-wrapper">
        <div className="keywords-list">
          {keywords.map((keyword, index) => {
            const isDoubleWeight = doubleWeightKeywords.includes(keyword);
            return (
              <span 
                key={index} 
                className={`keyword-tag ${isDoubleWeight ? 'double-weight' : ''}`}
              >
                {onDoubleWeightChange && (
                  <button
                    className={`keyword-weight-toggle ${isDoubleWeight ? 'active' : ''}`}
                    onClick={() => toggleDoubleWeight(keyword)}
                    type="button"
                    title={isDoubleWeight ? "Remove double weight" : "Make double weight (2x)"}
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill={isDoubleWeight ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                  </button>
                )}
                {keyword}
                <button
                  className="keyword-remove"
                  onClick={() => handleRemoveKeyword(index)}
                  type="button"
                >
                  ✕
                </button>
              </span>
            );
          })}
        </div>
        <input
          type="text"
          className="keyword-input"
          placeholder={
            keywords.length === 0
              ? "Type keywords (separate with comma or Enter)..."
              : "Add more..."
          }
          value={inputValue}
          onChange={(e) => handleInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
        />
      </div>
      <p className="keyword-hint">
        Press Enter or use commas to add keywords. Press Backspace to remove the
        last keyword.
        {onDoubleWeightChange && (
          <span className="double-weight-hint">
            {" "}Click the star to make a keyword count as 2x weight.
          </span>
        )}
      </p>
    </div>
  );
};

export default KeywordInput;
