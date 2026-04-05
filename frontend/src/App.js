import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState('');
  const [stageMessage, setStageMessage] = useState('');
  const [researchData, setResearchData] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [finalReport, setFinalReport] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Reset state
    setIsLoading(true);
    setError(null);
    setCurrentStage('');
    setStageMessage('');
    setResearchData(null);
    setAnalysisData(null);
    setFinalReport(null);

    try {
      const response = await fetch(`${API_URL}/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to start research');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Append new chunk to buffer
        buffer += decoder.decode(value, { stream: true });

        // Split by double newline (SSE message boundary)
        const messages = buffer.split('\n\n');

        // Keep the last incomplete message in the buffer
        buffer = messages.pop() || '';

        for (const message of messages) {
          const lines = message.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.type === 'start') {
                  setCurrentStage('initializing');
                  setStageMessage('Starting research pipeline...');
                } else if (data.type === 'stage') {
                  setCurrentStage(data.data.stage);
                  setStageMessage(data.data.message);

                  if (data.data.status === 'completed') {
                    if (data.data.stage === 'research') {
                      setResearchData(data.data.result);
                    } else if (data.data.stage === 'analysis') {
                      setAnalysisData(data.data.result);
                    }
                  }
                } else if (data.type === 'complete') {
                  setFinalReport(data.data);
                  setCurrentStage('completed');
                  setStageMessage('Research completed!');
                  setIsLoading(false);
                } else if (data.type === 'error') {
                  setError(data.data.message);
                  setIsLoading(false);
                }
              } catch (parseError) {
                console.error('Failed to parse SSE data:', parseError, 'Line:', line);
              }
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  const getStageIcon = (stage) => {
    if (stage === currentStage) return '⏳';
    if (stage === 'research' && researchData) return '✓';
    if (stage === 'analysis' && analysisData) return '✓';
    if (stage === 'writing' && finalReport) return '✓';
    return '○';
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>AI Research Pipeline</h1>
          <p>Multi-agent research, analysis, and reporting</p>
        </header>

        <form onSubmit={handleSubmit} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research question..."
            className="search-input"
            disabled={isLoading}
          />
          <button type="submit" className="search-button" disabled={isLoading}>
            {isLoading ? 'Researching...' : 'Research'}
          </button>
        </form>

        {isLoading && (
          <div className="progress">
            <div className="stage-indicator">
              <span className={currentStage === 'research' ? 'active' : ''}>
                {getStageIcon('research')} Research
              </span>
              <span className={currentStage === 'analysis' ? 'active' : ''}>
                {getStageIcon('analysis')} Analysis
              </span>
              <span className={currentStage === 'writing' ? 'active' : ''}>
                {getStageIcon('writing')} Writing
              </span>
            </div>
            <p className="stage-message">{stageMessage}</p>
          </div>
        )}

        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {researchData && (
          <div className="result-section">
            <h2>Research Findings</h2>
            <p className="summary">{researchData.summary}</p>
            <div className="sources">
              <h3>Sources ({researchData.sources.length})</h3>
              <ul>
                {researchData.sources.map((source, idx) => (
                  <li key={idx}>
                    <a href={source} target="_blank" rel="noopener noreferrer">
                      {source}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {analysisData && (
          <div className="result-section">
            <h2>Analysis</h2>
            <div className="analysis-grid">
              <div className="analysis-card">
                <h3>Trends</h3>
                <ul>
                  {analysisData.trends.map((trend, idx) => (
                    <li key={idx}>{trend}</li>
                  ))}
                </ul>
              </div>
              <div className="analysis-card">
                <h3>Risks</h3>
                <ul>
                  {analysisData.risks.map((risk, idx) => (
                    <li key={idx}>{risk}</li>
                  ))}
                </ul>
              </div>
              <div className="analysis-card">
                <h3>Key Insights</h3>
                <ul>
                  {analysisData.key_insights.map((insight, idx) => (
                    <li key={idx}>{insight}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {finalReport && (
          <div className="result-section final-report">
            <h2>Final Report</h2>

            <div className="executive-summary">
              <h3>Executive Summary</h3>
              <p>{finalReport.executive_summary}</p>
            </div>

            <div className="markdown-report">
              <ReactMarkdown>{finalReport.markdown_report}</ReactMarkdown>
            </div>

            <div className="follow-up">
              <h3>Follow-up Questions</h3>
              <ul>
                {finalReport.follow_up_questions.map((question, idx) => (
                  <li key={idx}>{question}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
