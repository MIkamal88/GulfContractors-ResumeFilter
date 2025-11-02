import React from 'react';
import type { ResumeAnalysis } from '../types';

interface ResultsProps {
  results: ResumeAnalysis[];
  totalResumes: number;
  passedResumes: number;
  csvPath?: string;
  onDownloadCSV?: () => void;
}

const Results: React.FC<ResultsProps> = ({
  results,
  totalResumes,
  passedResumes,
  csvPath,
  onDownloadCSV,
}) => {
  return (
    <div className="results-container">
      <div className="results-header">
        <h2>Analysis Results</h2>
        <div className="results-summary">
          <div className="summary-stat">
            <span className="stat-label">Total Resumes:</span>
            <span className="stat-value">{totalResumes}</span>
          </div>
          <div className="summary-stat">
            <span className="stat-label">Passed Filter:</span>
            <span className="stat-value passed">{passedResumes}</span>
          </div>
          <div className="summary-stat">
            <span className="stat-label">Pass Rate:</span>
            <span className="stat-value">
              {totalResumes > 0 ? ((passedResumes / totalResumes) * 100).toFixed(1) : 0}%
            </span>
          </div>
        </div>
        {csvPath && onDownloadCSV && (
          <button className="download-btn" onClick={onDownloadCSV}>
            Download CSV Report
          </button>
        )}
      </div>

      <div className="results-list">
        {results.map((result, index) => (
          <div key={index} className="result-card">
            <div className="result-header">
              <h3 className="result-filename">{result.filename}</h3>
              <div className="result-score">
                <span className="score-label">Score:</span>
                <span className={`score-value ${result.score >= 70 ? 'high' : result.score >= 40 ? 'medium' : 'low'}`}>
                  {result.score}
                </span>
              </div>
            </div>

            {result.keywords_found && result.keywords_found.length > 0 && (
              <div className="matched-keywords">
                <h4>Matched Keywords ({result.keywords_found.length}):</h4>
                <div className="keywords-tags">
                  {result.keywords_found.map((keyword, idx) => (
                    <span key={idx} className="keyword-badge">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {result.ai_summary && (
              <div className="ai-summary">
                <h4>AI Summary:</h4>
                <p>{result.ai_summary}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Results;
