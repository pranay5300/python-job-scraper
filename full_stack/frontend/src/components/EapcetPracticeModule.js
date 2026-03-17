import React, { useCallback, useEffect, useMemo, useState } from 'react';
import './EapcetPracticeModule.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://python-job-scraper.onrender.com';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const hasAnswerForQuestion = (answers, questionId) =>
  Object.prototype.hasOwnProperty.call(answers, questionId);

const formatTime = (totalSeconds) => {
  const safeSeconds = Math.max(totalSeconds || 0, 0);
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const seconds = safeSeconds % 60;

  return [hours, minutes, seconds]
    .map((value) => String(value).padStart(2, '0'))
    .join(':');
};

const buildPreviewBreakdown = (solutions) => {
  const summary = {
    Mathematics: { total: 0 },
    Physics: { total: 0 },
    Chemistry: { total: 0 }
  };

  solutions.forEach((solution) => {
    if (!summary[solution.subject]) {
      summary[solution.subject] = { total: 0 };
    }
    summary[solution.subject].total += 1;
  });

  return summary;
};

const EapcetPracticeModule = () => {
  const [overview, setOverview] = useState(null);
  const [view, setView] = useState('dashboard');
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [loadingPaperId, setLoadingPaperId] = useState(null);
  const [error, setError] = useState('');
  const [activePaper, setActivePaper] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [reviewFlags, setReviewFlags] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [resultPayload, setResultPayload] = useState(null);
  const [resultFilter, setResultFilter] = useState('all');
  const [candidateEmail, setCandidateEmail] = useState('');
  const [emailInput, setEmailInput] = useState('');
  const [emailPromptPaperId, setEmailPromptPaperId] = useState(null);
  const [emailPromptError, setEmailPromptError] = useState('');
  const [emailNotice, setEmailNotice] = useState(null);

  const fetchOverview = useCallback(async () => {
    setLoadingOverview(true);
    setError('');

    try {
      const response = await fetch(`${BACKEND_URL}/eapcet/overview`);

      if (!response.ok) {
        throw new Error(`Unable to load overview (${response.status})`);
      }

      const payload = await response.json();
      setOverview(payload);
    } catch (fetchError) {
      console.error('Failed to load EAPCET overview:', fetchError);
      setError(fetchError.message || 'Unable to load the TS EAPCET practice module.');
    } finally {
      setLoadingOverview(false);
    }
  }, []);

  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  const startPaper = useCallback(async (paperId, confirmedEmail) => {
    setLoadingPaperId(paperId);
    setError('');
    setEmailNotice(null);

    try {
      const response = await fetch(`${BACKEND_URL}/eapcet/papers/${paperId}`);

      if (!response.ok) {
        throw new Error(`Unable to load mock paper (${response.status})`);
      }

      const payload = await response.json();

      setActivePaper(payload);
      setAnswers({});
      setReviewFlags({});
      setCurrentQuestionIndex(0);
      setTimeRemaining(payload.durationMinutes * 60);
      setResultPayload(null);
      setResultFilter('all');
      setCandidateEmail(confirmedEmail);
      setView('exam');
    } catch (fetchError) {
      console.error('Failed to load paper:', fetchError);
      setError(fetchError.message || 'Unable to load the selected mock paper.');
    } finally {
      setLoadingPaperId(null);
    }
  }, []);

  const sendSolutionSheetEmail = useCallback(async (paperId, answersPayload, recipientEmail) => {
    const response = await fetch(`${BACKEND_URL}/eapcet/papers/${paperId}/email-solution`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: recipientEmail,
        answers: answersPayload
      })
    });

    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || `Unable to email the solution sheet (${response.status})`);
    }

    return payload;
  }, []);

  const submitPaper = useCallback(async (autoSubmitted = false) => {
    if (!activePaper || submitting) {
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const response = await fetch(`${BACKEND_URL}/eapcet/papers/${activePaper.paperId}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answers })
      });

      if (!response.ok) {
        throw new Error(`Unable to submit paper (${response.status})`);
      }

      const payload = await response.json();
      let nextEmailNotice = null;

      if (!autoSubmitted && candidateEmail) {
        const wantsEmail = window.confirm(
          `Do you want the detailed solution sheet emailed to ${candidateEmail}?`
        );

        if (wantsEmail) {
          try {
            const emailResponse = await sendSolutionSheetEmail(
              activePaper.paperId,
              answers,
              candidateEmail
            );
            nextEmailNotice = {
              type: 'success',
              message: emailResponse.message
            };
          } catch (emailError) {
            console.error('Failed to email solution sheet:', emailError);
            nextEmailNotice = {
              type: 'error',
              message: emailError.message || 'Unable to email the solution sheet.'
            };
          }
        }
      }

      setEmailNotice(nextEmailNotice);
      setResultPayload({
        ...payload,
        previewOnly: false,
        autoSubmitted,
        candidateEmail
      });
      setView('results');
    } catch (submitError) {
      console.error('Failed to submit paper:', submitError);
      setError(submitError.message || 'Unable to submit the mock paper.');
    } finally {
      setSubmitting(false);
    }
  }, [activePaper, answers, candidateEmail, sendSolutionSheetEmail, submitting]);

  useEffect(() => {
    if (view !== 'exam' || !activePaper) {
      return undefined;
    }

    if (timeRemaining === 0 && !submitting) {
      submitPaper(true);
      return undefined;
    }

    if (timeRemaining === null || timeRemaining <= 0) {
      return undefined;
    }

    const timer = window.setTimeout(() => {
      setTimeRemaining((previous) => (previous !== null ? previous - 1 : previous));
    }, 1000);

    return () => window.clearTimeout(timer);
  }, [activePaper, submitPaper, submitting, timeRemaining, view]);

  const currentQuestion = activePaper?.questions[currentQuestionIndex] || null;
  const answeredCount = activePaper
    ? activePaper.questions.filter((question) => hasAnswerForQuestion(answers, question.id)).length
    : 0;
  const markedCount = Object.values(reviewFlags).filter(Boolean).length;

  const resultSolutions = resultPayload?.solutions || [];
  const resultBreakdown = useMemo(() => {
    if (!resultPayload) {
      return null;
    }

    if (resultPayload.previewOnly) {
      return buildPreviewBreakdown(resultSolutions);
    }

    return resultPayload.subjectBreakdown;
  }, [resultPayload, resultSolutions]);

  const filteredSolutions = useMemo(() => {
    if (!resultPayload) {
      return [];
    }

    if (resultPayload.previewOnly || resultFilter === 'all') {
      return resultSolutions;
    }

    if (resultFilter === 'incorrect') {
      return resultSolutions.filter(
        (solution) => solution.selectedOption !== null && !solution.isCorrect
      );
    }

    if (resultFilter === 'unanswered') {
      return resultSolutions.filter((solution) => solution.selectedOption === null);
    }

    if (resultFilter === 'correct') {
      return resultSolutions.filter((solution) => solution.isCorrect);
    }

    return resultSolutions;
  }, [resultFilter, resultPayload, resultSolutions]);

  const handleSelectOption = (questionId, optionIndex) => {
    setAnswers((previous) => ({
      ...previous,
      [questionId]: optionIndex
    }));
  };

  const handleClearResponse = (questionId) => {
    setAnswers((previous) => {
      const updatedAnswers = { ...previous };
      delete updatedAnswers[questionId];
      return updatedAnswers;
    });
  };

  const toggleReviewFlag = (questionId) => {
    setReviewFlags((previous) => ({
      ...previous,
      [questionId]: !previous[questionId]
    }));
  };

  const goBackToDashboard = () => {
    setView('dashboard');
    setActivePaper(null);
    setAnswers({});
    setReviewFlags({});
    setTimeRemaining(null);
    setResultPayload(null);
    setError('');
  };

  const handleStartPaperRequest = (paperId) => {
    setEmailPromptPaperId(paperId);
    setEmailInput(candidateEmail);
    setEmailPromptError('');
  };

  const closeEmailPrompt = () => {
    setEmailPromptPaperId(null);
    setEmailPromptError('');
  };

  const handleConfirmStart = () => {
    const trimmedEmail = emailInput.trim();

    if (!EMAIL_REGEX.test(trimmedEmail)) {
      setEmailPromptError('Enter a valid email address to start the mock paper.');
      return;
    }

    const targetPaperId = emailPromptPaperId;
    setEmailPromptPaperId(null);
    setEmailPromptError('');
    setCandidateEmail(trimmedEmail);
    startPaper(targetPaperId, trimmedEmail);
  };

  const handleSubmitClick = () => {
    if (window.confirm('Submit this mock paper and open the detailed solution sheet?')) {
      submitPaper(false);
    }
  };

  const getPaletteStatus = (questionId, index) => {
    if (index === currentQuestionIndex) {
      return 'current';
    }

    if (reviewFlags[questionId] && hasAnswerForQuestion(answers, questionId)) {
      return 'review-answered';
    }

    if (reviewFlags[questionId]) {
      return 'review';
    }

    if (hasAnswerForQuestion(answers, questionId)) {
      return 'answered';
    }

    return 'unanswered';
  };

  if (loadingOverview) {
    return (
      <section className="exam-module-shell">
        <div className="exam-panel">
          <h2>Loading TS EAPCET practice module...</h2>
          <p>Fetching the paper model, knowledge bank summary, and mock papers.</p>
        </div>
      </section>
    );
  }

  if (view === 'results' && resultPayload) {
    return (
      <section className="exam-module-shell">
        <div className="exam-panel exam-results-panel">
          <div className="exam-results-header">
            <div>
              <p className="eyebrow">TS EAPCET engineering practice</p>
              <h2>{resultPayload.title}</h2>
              <p className="muted">
                Inspired by the {resultPayload.inspiredByYear} paper cycle.
              </p>
            </div>
            <div className="results-actions">
              <button className="secondary-button" onClick={goBackToDashboard}>
                Back to dashboard
              </button>
              <button
                className="primary-button"
                onClick={() => handleStartPaperRequest(resultPayload.paperId)}
              >
                {resultPayload.previewOnly ? 'Start this paper' : 'Retake this paper'}
              </button>
            </div>
          </div>

          {emailNotice && !resultPayload.previewOnly && (
            <div className={`inline-notice ${emailNotice.type}`}>
              {emailNotice.message}
            </div>
          )}

          <div className="results-summary-grid">
            <div className="metric-card">
              <span className="metric-label">
                {resultPayload.previewOnly ? 'Mode' : 'Score'}
              </span>
              <strong>
                {resultPayload.previewOnly
                  ? 'Solution sheet preview'
                  : `${resultPayload.score} / ${resultPayload.maxScore}`}
              </strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">
                {resultPayload.previewOnly ? 'Questions' : 'Attempted'}
              </span>
              <strong>
                {resultPayload.previewOnly
                  ? resultSolutions.length
                  : `${resultPayload.attempted} / ${resultPayload.maxScore}`}
              </strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">
                {resultPayload.previewOnly ? 'Coverage' : 'Overall percentage'}
              </span>
              <strong>
                {resultPayload.previewOnly
                  ? 'All explanations included'
                  : `${resultPayload.overallPercentage}%`}
              </strong>
            </div>
            {!resultPayload.previewOnly && (
              <div className="metric-card">
                <span className="metric-label">Submission type</span>
                <strong>{resultPayload.autoSubmitted ? 'Auto-submitted on timer end' : 'Submitted by user'}</strong>
              </div>
            )}
          </div>

          {resultBreakdown && (
            <div className="subject-breakdown-grid">
              {Object.entries(resultBreakdown).map(([subject, stats]) => (
                <div className="subject-breakdown-card" key={subject}>
                  <h3>{subject}</h3>
                  <p>
                    <strong>Total:</strong> {stats.total}
                  </p>
                  {!resultPayload.previewOnly && (
                    <>
                      <p>
                        <strong>Correct:</strong> {stats.correct}
                      </p>
                      <p>
                        <strong>Attempted:</strong> {stats.attempted}
                      </p>
                      <p>
                        <strong>Unanswered:</strong> {stats.unanswered}
                      </p>
                      <p>
                        <strong>Accuracy:</strong> {stats.accuracy}%
                      </p>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {!resultPayload.previewOnly && (
            <div className="solution-filter-bar">
              <button
                className={resultFilter === 'all' ? 'active-filter' : ''}
                onClick={() => setResultFilter('all')}
              >
                All
              </button>
              <button
                className={resultFilter === 'incorrect' ? 'active-filter' : ''}
                onClick={() => setResultFilter('incorrect')}
              >
                Incorrect
              </button>
              <button
                className={resultFilter === 'unanswered' ? 'active-filter' : ''}
                onClick={() => setResultFilter('unanswered')}
              >
                Unanswered
              </button>
              <button
                className={resultFilter === 'correct' ? 'active-filter' : ''}
                onClick={() => setResultFilter('correct')}
              >
                Correct
              </button>
            </div>
          )}

          <div className="solutions-list">
            {filteredSolutions.map((solution) => (
              <article className="solution-card" key={solution.id}>
                <div className="solution-card-header">
                  <div>
                    <p className="solution-question-meta">
                      Q{solution.questionNumber} · {solution.subject} · {solution.topic}
                    </p>
                    <h3>{solution.prompt}</h3>
                  </div>
                  {!resultPayload.previewOnly && (
                    <span className={`result-pill ${solution.isCorrect ? 'correct' : 'incorrect'}`}>
                      {solution.selectedOption === null
                        ? 'Unanswered'
                        : solution.isCorrect
                          ? 'Correct'
                          : 'Incorrect'}
                    </span>
                  )}
                </div>

                <ul className="solution-options">
                  {solution.options.map((option, optionIndex) => {
                    const isSelected = solution.selectedOption === optionIndex;
                    const isCorrect = solution.correctOption === optionIndex;
                    const itemClassName = [
                      'solution-option-item',
                      isCorrect ? 'correct-answer' : '',
                      isSelected && !isCorrect ? 'selected-wrong-answer' : '',
                      isSelected && isCorrect ? 'selected-correct-answer' : ''
                    ]
                      .filter(Boolean)
                      .join(' ');

                    return (
                      <li className={itemClassName} key={`${solution.id}-${optionIndex}`}>
                        <span>{String.fromCharCode(65 + optionIndex)}.</span>
                        <span>{option}</span>
                      </li>
                    );
                  })}
                </ul>

                <div className="solution-explanation">
                  {!resultPayload.previewOnly && (
                    <>
                      <p>
                        <strong>Your answer:</strong>{' '}
                        {solution.selectedOptionText || 'Not answered'}
                      </p>
                      <p>
                        <strong>Correct answer:</strong> {solution.correctOptionText}
                      </p>
                    </>
                  )}
                  <p>
                    <strong>Explanation:</strong> {solution.explanation}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (view === 'exam' && activePaper && currentQuestion) {
    return (
      <section className="exam-module-shell">
        <div className="exam-layout">
          <aside className="exam-sidebar">
            <div className="exam-panel">
              <p className="eyebrow">Live mock paper</p>
              <h2>{activePaper.title}</h2>
              <p className="muted">Inspired by the {activePaper.inspiredByYear} paper cycle.</p>
              {candidateEmail && (
                <p className="candidate-email-pill">
                  Candidate email: {candidateEmail}
                </p>
              )}
              <div className="timer-card">
                <span className="metric-label">Time remaining</span>
                <strong>{formatTime(timeRemaining)}</strong>
              </div>
              <div className="exam-stats">
                <div>
                  <span className="metric-label">Answered</span>
                  <strong>{answeredCount}</strong>
                </div>
                <div>
                  <span className="metric-label">Marked</span>
                  <strong>{markedCount}</strong>
                </div>
                <div>
                  <span className="metric-label">Total</span>
                  <strong>{activePaper.totalQuestions}</strong>
                </div>
              </div>
              <div className="section-breakup">
                {activePaper.sections.map((section) => (
                  <p key={section.subject}>
                    <strong>{section.subject}:</strong> {section.questions} questions
                  </p>
                ))}
              </div>
              <div className="sidebar-actions">
                <button className="secondary-button" onClick={goBackToDashboard}>
                  Leave exam
                </button>
                <button className="primary-button" onClick={handleSubmitClick} disabled={submitting}>
                  {submitting ? 'Submitting...' : 'Submit paper'}
                </button>
              </div>
            </div>

            <div className="exam-panel">
              <h3>Question palette</h3>
              <div className="question-palette">
                {activePaper.questions.map((question, index) => (
                  <button
                    className={`palette-item ${getPaletteStatus(question.id, index)}`}
                    key={question.id}
                    onClick={() => setCurrentQuestionIndex(index)}
                    type="button"
                  >
                    {question.questionNumber}
                  </button>
                ))}
              </div>
            </div>
          </aside>

          <div className="exam-panel exam-question-panel">
            <div className="question-header-row">
              <div>
                <p className="question-tag-row">
                  <span className="subject-tag">{currentQuestion.subject}</span>
                  <span className="topic-tag">{currentQuestion.topic}</span>
                  <span className="difficulty-tag">{currentQuestion.difficulty}</span>
                </p>
                <h2>
                  Question {currentQuestion.questionNumber} of {activePaper.totalQuestions}
                </h2>
              </div>
              <button
                className={`review-toggle ${reviewFlags[currentQuestion.id] ? 'active-review' : ''}`}
                onClick={() => toggleReviewFlag(currentQuestion.id)}
                type="button"
              >
                {reviewFlags[currentQuestion.id] ? 'Marked for review' : 'Mark for review'}
              </button>
            </div>

            <div className="question-stem">
              <p>{currentQuestion.prompt}</p>
            </div>

            <div className="option-list">
              {currentQuestion.options.map((option, optionIndex) => {
                const isSelected = answers[currentQuestion.id] === optionIndex;
                return (
                  <button
                    className={`option-button ${isSelected ? 'selected-option' : ''}`}
                    key={`${currentQuestion.id}-${optionIndex}`}
                    onClick={() => handleSelectOption(currentQuestion.id, optionIndex)}
                    type="button"
                  >
                    <span className="option-badge">{String.fromCharCode(65 + optionIndex)}</span>
                    <span>{option}</span>
                  </button>
                );
              })}
            </div>

            <div className="question-footer-actions">
              <button
                className="secondary-button"
                onClick={() => setCurrentQuestionIndex((previous) => Math.max(previous - 1, 0))}
                disabled={currentQuestionIndex === 0}
                type="button"
              >
                Previous
              </button>
              <button
                className="secondary-button"
                onClick={() => handleClearResponse(currentQuestion.id)}
                type="button"
              >
                Clear response
              </button>
              <button
                className="secondary-button"
                onClick={() =>
                  setCurrentQuestionIndex((previous) =>
                    Math.min(previous + 1, activePaper.totalQuestions - 1)
                  )
                }
                disabled={currentQuestionIndex === activePaper.totalQuestions - 1}
                type="button"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="exam-module-shell">
      <div className="exam-dashboard-grid">
        <div className="exam-panel overview-panel">
          <p className="eyebrow">TS EAPCET Engineering mock practice</p>
          <h2>Official pattern aligned mock exam workspace</h2>
          <p className="muted">
            Practice against 10 full-length mock papers that follow the official TS EAPCET engineering
            paper model while using original explanation-rich questions.
          </p>

          {error && <div className="inline-error">{error}</div>}

          <div className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">Duration</span>
              <strong>{overview?.exam?.duration_minutes} minutes</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Total questions</span>
              <strong>{overview?.exam?.total_questions}</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Marking</span>
              <strong>+1 per correct, no negative marks</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Languages</span>
              <strong>{overview?.exam?.languages?.join(', ')}</strong>
            </div>
          </div>

          <div className="instruction-card-grid">
            <div className="support-card">
              <h3>Paper model</h3>
              {overview?.exam?.sections?.map((section) => (
                <p key={section.subject}>
                  <strong>{section.subject}:</strong> {section.questions} questions
                </p>
              ))}
            </div>
            <div className="support-card">
              <h3>Knowledge bank</h3>
              <p>
                <strong>Years covered:</strong> {overview?.knowledgeBank?.yearsCovered?.join(', ')}
              </p>
              <p>
                <strong>Total original practice questions:</strong>{' '}
                {overview?.knowledgeBank?.totalOriginalPracticeQuestions}
              </p>
            </div>
          </div>

          <div className="support-card">
            <h3>Practice instructions</h3>
            <ul className="instruction-list">
              {overview?.exam?.instructions?.map((instruction) => (
                <li key={instruction}>{instruction}</li>
              ))}
            </ul>
          </div>

          <div className="support-card">
            <h3>Official source references</h3>
            {overview?.exam?.official_sources?.map((source) => (
              <div className="source-row" key={source.url}>
                <a href={source.url} rel="noreferrer" target="_blank">
                  {source.title}
                </a>
                <p>{source.note}</p>
              </div>
            ))}
          </div>

          <div className="support-card">
            <h3>Topic coverage</h3>
            <div className="topic-columns">
              {Object.entries(overview?.knowledgeBank?.topicCoverage || {}).map(([subject, topics]) => (
                <div key={subject}>
                  <h4>{subject}</h4>
                  <p>{topics.join(', ')}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="exam-panel">
          <h2>Available mock papers</h2>
          <div className="mock-paper-list">
            {overview?.mockPapers?.map((paper) => (
              <article className="mock-paper-card" key={paper.paperId}>
                <div className="mock-paper-card-header">
                  <div>
                    <p className="eyebrow">Paper {paper.paperId}</p>
                    <h3>{paper.title}</h3>
                    <p className="muted">Inspired by the {paper.inspiredByYear} paper cycle</p>
                  </div>
                  <span className="question-count-pill">{paper.totalQuestions} questions</span>
                </div>

                <div className="focus-grid">
                  {Object.entries(paper.focus).map(([subject, topics]) => (
                    <div className="focus-card" key={`${paper.paperId}-${subject}`}>
                      <strong>{subject}</strong>
                      <p>{topics.join(', ')}</p>
                    </div>
                  ))}
                </div>

                <div className="paper-card-actions">
                  <button
                    className="primary-button"
                    disabled={loadingPaperId === paper.paperId}
                    onClick={() => handleStartPaperRequest(paper.paperId)}
                    type="button"
                  >
                    {loadingPaperId === paper.paperId ? 'Loading...' : 'Start mock paper'}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>

      {emailPromptPaperId !== null && (
        <div className="modal-backdrop" role="presentation">
          <div className="email-modal" role="dialog" aria-modal="true" aria-labelledby="email-modal-title">
            <p className="eyebrow">Before you start</p>
            <h3 id="email-modal-title">Enter your email address</h3>
            <p className="muted">
              We will use this email address if you choose to receive the solution sheet after submission.
            </p>
            <label className="email-modal-label" htmlFor="candidate-email-input">
              Email address
            </label>
            <input
              id="candidate-email-input"
              className="email-modal-input"
              type="email"
              value={emailInput}
              onChange={(event) => setEmailInput(event.target.value)}
              placeholder="you@example.com"
            />
            {emailPromptError && (
              <div className="inline-error">{emailPromptError}</div>
            )}
            <div className="paper-card-actions">
              <button
                className="primary-button"
                onClick={handleConfirmStart}
                type="button"
              >
                Continue to mock paper
              </button>
              <button
                className="secondary-button"
                onClick={closeEmailPrompt}
                type="button"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default EapcetPracticeModule;
