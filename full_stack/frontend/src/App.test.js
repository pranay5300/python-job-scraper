import { render, screen } from '@testing-library/react';
import App from './App';

test('renders public mock exam dashboard', async () => {
  global.fetch = jest.fn((url) => {
    if (String(url).includes('/eapcet/overview')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({
          exam: {
            duration_minutes: 180,
            total_questions: 160,
            languages: ['English', 'Telugu', 'Urdu'],
            sections: [
              { subject: 'Mathematics', questions: 80 },
              { subject: 'Physics', questions: 40 },
              { subject: 'Chemistry', questions: 40 }
            ],
            instructions: ['Follow the official pattern.'],
            official_sources: [
              {
                title: 'TS EAPCET official portal',
                url: 'https://eapcet.tgche.ac.in/',
                note: 'Check the official portal for the latest bulletin.'
              }
            ]
          },
          knowledgeBank: {
            yearsCovered: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
            totalOriginalPracticeQuestions: 1600,
            topicCoverage: {
              Mathematics: ['Progressions'],
              Physics: ['Kinematics'],
              Chemistry: ['Atomic Structure']
            }
          },
          mockPapers: [
            {
              paperId: 1,
              title: 'Mock Paper 1',
              inspiredByYear: 2015,
              totalQuestions: 160,
              focus: {
                Mathematics: ['Progressions'],
                Physics: ['Kinematics'],
                Chemistry: ['Atomic Structure']
              }
            }
          ]
        })
      });
    }

    if (String(url).includes('/health')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ status: 'healthy' })
      });
    }

    if (String(url).includes('/job_market_analytics')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ success: true, data: {} })
      });
    }

    return Promise.resolve({
      ok: true,
      json: async () => ({})
    });
  });

  render(<App />);
  const headingElement = await screen.findByText(/Official pattern aligned mock exam workspace/i);
  expect(headingElement).toBeInTheDocument();
  expect(screen.queryByText(/job search tools/i)).not.toBeInTheDocument();
});
