import { useState, lazy, Suspense } from "react";
import "./App.css";
import FileUpload from "./components/FileUpload";
import KeywordInput from "./components/KeywordInput";
import JobProfileSelector from "./components/JobProfileSelector";
import { filterResumes, downloadCSV } from "./services/api";
import type { FilterResponse } from "./types";


// Lazy load Results component since it's only needed after form submission
const Results = lazy(() => import("./components/Results"));

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [doubleWeightKeywords, setDoubleWeightKeywords] = useState<string[]>([]);
  const [minScore, setMinScore] = useState<string>("");
  const [generateAiSummary, setGenerateAiSummary] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<FilterResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [selectedJobProfileName, setSelectedJobProfileName] = useState<string | null>(null);

  const handleFilesSelected = (selectedFiles: File[]) => {
    setFiles(selectedFiles);
    setError(null);
  };

  const handleKeywordsChange = (newKeywords: string[]) => {
    setKeywords(newKeywords);
  };

  const handleProfileSelect = (
    profileKeywords: string[],
    profileName?: string,
    profileDoubleWeightKeywords?: string[]
  ) => {
    setKeywords(profileKeywords);
    setDoubleWeightKeywords(profileDoubleWeightKeywords || []);
    setSelectedJobProfileName(profileName || null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (files.length === 0) {
      setError("Please select at least one resume file");
      return;
    }

    if (keywords.length === 0) {
      setError("Please add at least one keyword");
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await filterResumes(
        files,
        keywords,
        minScore === "" ? 0 : Number(minScore),
        generateAiSummary,
        doubleWeightKeywords,
      );

      // Set results to show the Results page
      setResults(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred while processing resumes",
      );
      console.error("Error filtering resumes:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = async () => {
    if (!results?.candidates || results.candidates.length === 0) return;

    try {
      const blob = await downloadCSV(results.candidates);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `filtered_resumes_${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError("Failed to download CSV file");
      console.error("Error downloading CSV:", err);
    }
  };

  const handleReset = () => {
    setFiles([]);
    setKeywords([]);
    setDoubleWeightKeywords([]);
    setMinScore("");
    setGenerateAiSummary(true);
    setResults(null);
    setError(null);
    setSelectedJobProfileName(null);
  };

  return (
    <div className={`app ${darkMode ? "dark-mode" : ""}`}>
      <button
        className="dark-mode-toggle"
        onClick={() => setDarkMode(!darkMode)}
        aria-label="Toggle dark mode"
        title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
      >
        {darkMode ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        )}
      </button>

      <main className="app-main">
        {!results ? (
          <form onSubmit={handleSubmit} className="upload-form">
            <div className="form-section">
              <FileUpload onFilesSelected={handleFilesSelected} files={files} />
            </div>

            <div className="form-section">
              <JobProfileSelector
                onProfileSelect={handleProfileSelect}
                onError={setError}
              />
            </div>

            <div className="form-section">
              <KeywordInput
                keywords={keywords}
                onKeywordsChange={handleKeywordsChange}
                doubleWeightKeywords={doubleWeightKeywords}
                onDoubleWeightChange={setDoubleWeightKeywords}
              />
            </div>

            <div className="form-section">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="minScore">Minimum Score</label>
                  <input
                    type="number"
                    id="minScore"
                    min="0"
                    max="100"
                    value={minScore}
                    onChange={(e) => setMinScore(e.target.value)}
                    className="score-input"
                    placeholder="0"
                  />
                  <p className="input-hint">
                    Filter resumes with score above this threshold (0-100)
                  </p>
                </div>

                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={generateAiSummary}
                      onChange={(e) => setGenerateAiSummary(e.target.checked)}
                    />
                    <span>Generate AI Summary</span>
                  </label>
                  <p className="input-hint">
                    Enable OpenAI-powered resume summaries
                  </p>
                </div>
              </div>
            </div>

            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <div className="form-actions">
              <button type="submit" className="submit-btn" disabled={loading}>
                {loading ? (
                  <>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ animation: 'spin 1s linear infinite' }}>
                      <line x1="12" y1="2" x2="12" y2="6"/>
                      <line x1="12" y1="18" x2="12" y2="22"/>
                      <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
                      <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                      <line x1="2" y1="12" x2="6" y2="12"/>
                      <line x1="18" y1="12" x2="22" y2="12"/>
                      <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
                      <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
                    </svg>
                    Processing...
                  </>
                ) : (
                  <>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="11" cy="11" r="8"/>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                    </svg>
                    Analyze Resumes
                  </>
                )}
              </button>
            </div>
          </form>
        ) : (
          <Suspense fallback={<div className="loading-message">Loading results...</div>}>
            <Results
              results={results.candidates}
              totalResumes={results.total_resumes}
              passedResumes={results.valid_candidates}
              onDownloadCSV={handleDownloadCSV}
              jobProfileName={selectedJobProfileName}
            />
            <div className="form-actions">
              <button onClick={handleReset} className="reset-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="1 4 1 10 7 10"/>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                </svg>
                Analyze More Resumes
              </button>
            </div>
          </Suspense>
        )}
      </main>

    </div>
  );
}

export default App;
