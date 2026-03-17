import unittest

from app import app


class EapcetApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_overview_matches_official_pattern(self):
        response = self.client.get('/eapcet/overview')
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertEqual(payload['exam']['total_questions'], 160)
        self.assertEqual(payload['exam']['duration_minutes'], 180)
        self.assertEqual(payload['knowledgeBank']['totalMockPapers'], 10)

    def test_mock_paper_payload_hides_answers(self):
        response = self.client.get('/eapcet/papers/1')
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertEqual(len(payload['questions']), 160)
        self.assertNotIn('correctOption', payload['questions'][0])
        self.assertEqual(payload['questions'][79]['subject'], 'Mathematics')
        self.assertEqual(payload['questions'][80]['subject'], 'Physics')
        self.assertEqual(payload['questions'][120]['subject'], 'Chemistry')

    def test_solution_sheet_and_perfect_submission(self):
        solution_response = self.client.get('/eapcet/papers/1/solutions')
        self.assertEqual(solution_response.status_code, 200)
        solution_payload = solution_response.get_json()
        self.assertEqual(len(solution_payload['solutionSheet']), 160)
        self.assertIn('explanation', solution_payload['solutionSheet'][0])

        answers = {
            solution['id']: solution['correctOption']
            for solution in solution_payload['solutionSheet']
        }

        submit_response = self.client.post('/eapcet/papers/1/submit', json={'answers': answers})
        self.assertEqual(submit_response.status_code, 200)

        submit_payload = submit_response.get_json()
        self.assertEqual(submit_payload['score'], 160)
        self.assertEqual(submit_payload['attempted'], 160)
        self.assertEqual(submit_payload['subjectBreakdown']['Mathematics']['correct'], 80)
        self.assertEqual(submit_payload['subjectBreakdown']['Physics']['correct'], 40)
        self.assertEqual(submit_payload['subjectBreakdown']['Chemistry']['correct'], 40)


if __name__ == '__main__':
    unittest.main()
