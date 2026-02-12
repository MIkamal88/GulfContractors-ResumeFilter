import React, { useRef, useState } from "react";
import type { ResumeAnalysis } from "../types";
import { openResume } from "../services/api";

interface ResultsProps {
  results: ResumeAnalysis[];
  totalResumes: number;
  passedResumes: number;
  onDownloadCSV?: () => void;
  jobProfileName?: string | null;
}

const Results: React.FC<ResultsProps> = ({
  results,
  totalResumes,
  passedResumes,
  onDownloadCSV,
  jobProfileName,
}) => {
  const resultsRef = useRef<HTMLDivElement>(null);
  const [expandedHistory, setExpandedHistory] = useState<Set<number>>(new Set());

  const handleOpenResume = (filename: string) => {
    openResume(filename);
  };

  const toggleHistory = (index: number) => {
    setExpandedHistory((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const handleExportPDF = async () => {
    if (!resultsRef.current) return;

    try {
      const element = resultsRef.current;

      // Add pdf-exporting class to hide buttons and force-show accordions via CSS
      element.classList.add('pdf-exporting');

      // Wait for DOM to update
      await new Promise((resolve) => setTimeout(resolve, 150));

      // Dynamically import html2pdf
      const html2pdf = (await import('html2pdf.js')).default;
      
      const opt = {
        margin: 10,
        filename: `resume_analysis_${new Date().toISOString().split("T")[0]}.pdf`,
        image: { type: 'jpeg' as const, quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' as const },
        pagebreak: { mode: ['css', 'legacy'] }
      };

      await html2pdf().set(opt).from(element).save();

      // Remove pdf-exporting class to restore normal UI
      element.classList.remove('pdf-exporting');
    } catch (error) {
      console.error('Error generating PDF:', error);
      if (resultsRef.current) {
        resultsRef.current.classList.remove('pdf-exporting');
      }
      alert('Failed to generate PDF. Please try again.');
    }
  };
  return (
    <div className="results-container" ref={resultsRef}>
      <div className="results-header">
        <h2>
          Analysis Results
          {jobProfileName && <span className="job-profile-badge"> - {jobProfileName}</span>}
        </h2>
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
              {totalResumes > 0
                ? ((passedResumes / totalResumes) * 100).toFixed(1)
                : 0}
              %
            </span>
          </div>
        </div>
        {results.length > 0 && (
          <div className="export-buttons">
            {onDownloadCSV && (
              <button className="download-btn" onClick={onDownloadCSV}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Download CSV
              </button>
            )}
            <button className="download-btn pdf-btn" onClick={handleExportPDF}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              Export PDF
            </button>
          </div>
        )}
      </div>

      <div className="results-list">
        {results.map((result, index) => (
          <div key={index} className="result-card">
            <div className="result-header">
              <div className="result-filename-section">
                <h3 className="result-filename">{result.filename}</h3>
                <button
                  className="open-resume-btn"
                  onClick={() => handleOpenResume(result.filename)}
                  title="Open resume in new tab"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15 3 21 3 21 9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                  </svg>
                  Open Resume
                </button>
              </div>
              <div className="result-score">
                <span className="score-label">Score:</span>
                {result.is_image_based ? (
                  <span 
                    className="score-value image-based" 
                    title="This resume appears to be image-based (scanned document). Text could not be extracted for scoring."
                  >
                    N/A
                  </span>
                ) : (
                  <span
                    className={`score-value ${result.score >= 70 ? "high" : result.score >= 40 ? "medium" : "low"}`}
                  >
                    {result.score}
                  </span>
                )}
                
                {result.is_image_based ? (
                  <span 
                    className="uae-badge image-based"
                    title="UAE presence could not be determined for image-based resumes."
                  >
                    UAE: N/A
                  </span>
                ) : result.uae_presence !== undefined && (
                  <span className={`uae-badge ${result.uae_presence ? "in-uae" : "not-in-uae"}`}>
                    {result.uae_presence ? (
                      <>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                        UAE
                      </>
                    ) : (
                      <>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <line x1="18" y1="6" x2="6" y2="18"/>
                          <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                        UAE
                      </>
                    )}
                  </span>
                )}
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

            {result.is_image_based ? (
              <div className="image-based-notice">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>This resume appears to be image-based (scanned document). Text could not be extracted for analysis.</span>
              </div>
            ) : result.ai_summary && (
              <div className="ai-summary">
                <h4>AI Summary:</h4>
                <div className="ai-summary-content">
                  {result.ai_summary.split('\n').map((line, idx) => (
                    line.trim() && <p key={idx}>{line}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Employment History Accordion */}
            {result.employment_history && result.employment_history.length > 0 && (
              <div
                className="employment-history-section"
                data-pdf-title={`Employment History (${result.employment_history.length} positions${result.total_experience_years != null ? ` - ${result.total_experience_years} years total` : ''})`}
              >
                <button
                  className={`employment-accordion-toggle ${expandedHistory.has(index) ? 'expanded' : ''}`}
                  onClick={() => toggleHistory(index)}
                  type="button"
                >
                  <svg className="accordion-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="6 9 12 15 18 9"/>
                  </svg>
                  <h4>
                    Employment History ({result.employment_history.length} positions
                    {result.total_experience_years != null && (
                      <span className="total-exp-inline"> - {result.total_experience_years} years total</span>
                    )})
                  </h4>
                </button>

                <div className={`employment-accordion-content ${expandedHistory.has(index) ? 'expanded' : ''}`}>
                  <table className="employment-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Company - Location - Role</th>
                        <th>Period</th>
                        <th>Years</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.employment_history.map((entry, idx) => (
                        <tr key={idx}>
                          <td className="emp-index">{idx + 1}</td>
                          <td className="emp-detail">
                            <span className="emp-company">{entry.company}</span>
                            {" - "}
                            <span className="emp-location">{entry.location}</span>
                            {" - "}
                            <span className="emp-role">{entry.role}</span>
                          </td>
                          <td className="emp-period">{entry.start_date} - {entry.end_date}</td>
                          <td className="emp-duration">{entry.duration_years}</td>
                        </tr>
                      ))}
                    </tbody>
                    {result.total_experience_years != null && (
                      <tfoot>
                        <tr className="emp-total-row">
                          <td colSpan={3} className="emp-total-label">Total Experience</td>
                          <td className="emp-total-value">{result.total_experience_years}</td>
                        </tr>
                      </tfoot>
                    )}
                  </table>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Results;








