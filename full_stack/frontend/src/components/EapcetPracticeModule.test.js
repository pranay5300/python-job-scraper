import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import EapcetPracticeModule from './EapcetPracticeModule';

const overviewPayload = {
  exam: {
    duration_minutes: 180,
    total_questions: 160,
    languages: ['English', 'Telugu', 'Urdu'],
    sections: [
      { subject: 'Mathematics', questions: 80 },
      { subject: 'Physics', questions: 40 },
      { subject: 'Chemistry', questions: 40 }
    ],
    instructions: ['Follow the official pattern.', 'No negative marking.'],
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
      Mathematics: ['Progressions', 'Calculus'],
      Physics: ['Kinematics', 'Optics'],
      Chemistry: ['Atomic Structure', 'Bonding']
    }
  },
  mockPapers: [
    {
      paperId: 1,
      title: 'Mock Paper 1',
      inspiredByYear: 2015,
      totalQuestions: 160,
      focus: {
        Mathematics: ['Progressions', 'Coordinate Geometry'],
        Physics: ['Kinematics', 'Optics'],
        Chemistry: ['Atomic Structure', 'Bonding']
      }
    }
  ]
};

const paperPayload = {
  paperId: 1,
  title: 'Mock Paper 1',
  inspiredByYear: 2015,
  durationMinutes: 180,
  totalQuestions: 2,
  sections: [
    { subject: 'Mathematics', questions: 1 },
    { subject: 'Physics', questions: 1 },
    { subject: 'Chemistry', questions: 0 }
  ],
  instructions: ['Follow the official pattern.', 'No negative marking.'],
  focus: {
    Mathematics: ['Progressions'],
    Physics: ['Kinematics'],
    Chemistry: ['Atomic Structure']
  },
  questions: [
    {
      id: 'P1-1',
      questionNumber: 1,
      subject: 'Mathematics',
      topic: 'Progressions',
      difficulty: 'easy',
      prompt: 'The next term after 2, 4, 6 is',
      options: ['8', '7', '9', '10']
    },
    {
      id: 'P1-2',
      questionNumber: 2,
      subject: 'Physics',
      topic: 'Kinematics',
      difficulty: 'medium',
      prompt: 'Distance covered by a body at rest after 2 s with acceleration 2 m/s^2 is',
      options: ['4 m', '2 m', '6 m', '8 m']
    }
  ]
};

const submitPayload = {
  paperId: 1,
  title: 'Mock Paper 1',
  inspiredByYear: 2015,
  score: 1,
  maxScore: 2,
  attempted: 2,
  unanswered: 0,
  accuracy: 50,
  overallPercentage: 50,
  subjectBreakdown: {
    Mathematics: {
      correct: 1,
      attempted: 1,
      total: 1,
      unanswered: 0,
      accuracy: 100
    },
    Physics: {
      correct: 0,
      attempted: 1,
      total: 1,
      unanswered: 0,
      accuracy: 0
    },
    Chemistry: {
      correct: 0,
      attempted: 0,
      total: 0,
      unanswered: 0,
      accuracy: 0
    }
  },
  solutions: [
    {
      id: 'P1-1',
      questionNumber: 1,
      subject: 'Mathematics',
      topic: 'Progressions',
      difficulty: 'easy',
      prompt: 'The next term after 2, 4, 6 is',
      options: ['8', '7', '9', '10'],
      selectedOption: 0,
      selectedOptionText: '8',
      correctOption: 0,
      correctOptionText: '8',
      isCorrect: true,
      explanation: 'This is an arithmetic progression with common difference 2.'
    },
    {
      id: 'P1-2',
      questionNumber: 2,
      subject: 'Physics',
      topic: 'Kinematics',
      difficulty: 'medium',
      prompt: 'Distance covered by a body at rest after 2 s with acceleration 2 m/s^2 is',
      options: ['4 m', '2 m', '6 m', '8 m'],
      selectedOption: 1,
      selectedOptionText: '2 m',
      correctOption: 0,
      correctOptionText: '4 m',
      isCorrect: false,
      explanation: 'Use s = ut + (1/2)at^2 with u = 0, a = 2 and t = 2.'
    }
  ]
};

const emailPayload = {
  success: true,
  message: 'Solution sheet emailed to student@example.com.',
  recipientEmail: 'student@example.com'
};

describe('EapcetPracticeModule', () => {
  beforeEach(() => {
    global.fetch = jest.fn((url) => {
      if (url.endsWith('/eapcet/overview')) {
        return Promise.resolve({
          ok: true,
          json: async () => overviewPayload
        });
      }

      if (url.endsWith('/eapcet/papers/1')) {
        return Promise.resolve({
          ok: true,
          json: async () => paperPayload
        });
      }

      if (url.endsWith('/eapcet/papers/1/submit')) {
        return Promise.resolve({
          ok: true,
          json: async () => submitPayload
        });
      }

      if (url.endsWith('/eapcet/papers/1/email-solution')) {
        return Promise.resolve({
          ok: true,
          json: async () => emailPayload
        });
      }

      return Promise.reject(new Error(`Unhandled fetch request: ${url}`));
    });

    jest.spyOn(window, 'confirm').mockImplementation(() => true);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('captures email before starting and emails the solution sheet after submission', async () => {
    render(<EapcetPracticeModule />);

    expect(
      await screen.findByText(/Official pattern aligned mock exam workspace/i)
    ).toBeInTheDocument();

    expect(screen.queryByRole('button', { name: /view solution sheet/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /start mock paper/i }));
    expect(await screen.findByText(/Enter your email address/i)).toBeInTheDocument();
    fireEvent.change(screen.getByPlaceholderText('you@example.com'), {
      target: { value: 'student@example.com' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Continue to mock paper/i }));

    expect(await screen.findByText(/Question 1 of 2/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /8/i }));
    fireEvent.click(screen.getByRole('button', { name: /Next/i }));
    fireEvent.click(screen.getByRole('button', { name: /2 m/i }));
    fireEvent.click(screen.getByRole('button', { name: /Submit paper/i }));

    expect(await screen.findByText('1 / 2')).toBeInTheDocument();
    expect(screen.getByText(/Solution sheet emailed to student@example.com/i)).toBeInTheDocument();
    expect(screen.getByText(/This is an arithmetic progression/i)).toBeInTheDocument();
    expect(screen.getByText(/Use s = ut \+ \(1\/2\)at\^2/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/eapcet/papers/1/submit'),
        expect.objectContaining({ method: 'POST' })
      );
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/eapcet/papers/1/email-solution'),
        expect.objectContaining({ method: 'POST' })
      );
    });
  });
});
