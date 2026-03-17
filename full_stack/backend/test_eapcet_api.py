import unittest
import os
import sys
import smtplib
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

from app import app, send_eapcet_solution_email


class EapcetApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.paper_one_access_key = 'ats1'

    def test_overview_matches_official_pattern(self):
        response = self.client.get('/eapcet/overview')
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertEqual(payload['exam']['total_questions'], 160)
        self.assertEqual(payload['exam']['duration_minutes'], 180)
        self.assertEqual(payload['knowledgeBank']['totalMockPapers'], 10)

    def test_mock_paper_payload_hides_answers(self):
        response = self.client.get(f'/eapcet/papers/1?access_key={self.paper_one_access_key}')
        self.assertEqual(response.status_code, 200)

        payload = response.get_json()
        self.assertEqual(len(payload['questions']), 160)
        self.assertNotIn('correctOption', payload['questions'][0])
        self.assertEqual(payload['questions'][79]['subject'], 'Mathematics')
        self.assertEqual(payload['questions'][80]['subject'], 'Physics')
        self.assertEqual(payload['questions'][120]['subject'], 'Chemistry')

    def test_solution_sheet_and_perfect_submission(self):
        solution_response = self.client.get(
            f'/eapcet/papers/1/solutions?access_key={self.paper_one_access_key}'
        )
        self.assertEqual(solution_response.status_code, 200)
        solution_payload = solution_response.get_json()
        self.assertEqual(len(solution_payload['solutionSheet']), 160)
        self.assertIn('explanation', solution_payload['solutionSheet'][0])

        answers = {
            solution['id']: solution['correctOption']
            for solution in solution_payload['solutionSheet']
        }

        submit_response = self.client.post('/eapcet/papers/1/submit', json={
            'answers': answers,
            'candidateName': 'Student One',
            'accessKey': self.paper_one_access_key
        })
        self.assertEqual(submit_response.status_code, 200)

        submit_payload = submit_response.get_json()
        self.assertEqual(submit_payload['score'], 160)
        self.assertEqual(submit_payload['attempted'], 160)
        self.assertEqual(submit_payload['candidateName'], 'Student One')
        self.assertEqual(submit_payload['subjectBreakdown']['Mathematics']['correct'], 80)
        self.assertEqual(submit_payload['subjectBreakdown']['Physics']['correct'], 40)
        self.assertEqual(submit_payload['subjectBreakdown']['Chemistry']['correct'], 40)

    def test_mock_paper_requires_correct_password(self):
        response = self.client.get('/eapcet/papers/1?access_key=wrong-key')
        self.assertEqual(response.status_code, 403)
        self.assertIn('Invalid access key', response.get_json()['error'])

    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_SENDER_PASSWORD': 'test-password'
    }, clear=False)
    @patch('app.smtplib.SMTP')
    def test_solution_sheet_email_endpoint(self, smtp_mock):
        solution_response = self.client.get(
            f'/eapcet/papers/1/solutions?access_key={self.paper_one_access_key}'
        )
        solution_payload = solution_response.get_json()
        answers = {
            solution['id']: solution['correctOption']
            for solution in solution_payload['solutionSheet']
        }

        response = self.client.post('/eapcet/papers/1/email-solution', json={
            'email': 'student@example.com',
            'answers': answers,
            'candidateName': 'Student One',
            'accessKey': self.paper_one_access_key
        })

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['recipientEmail'], 'student@example.com')
        smtp_mock.assert_called_once()

    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_SENDER_PASSWORD': 'abcd efgh ijkl mnop',
        'SMTP_HOST': 'smtp.gmail.com',
        'SMTP_PORT': '587'
    }, clear=False)
    @patch('app.smtplib.SMTP')
    def test_gmail_password_spaces_are_normalized(self, smtp_mock):
        result_payload = self.client.post('/eapcet/papers/1/submit', json={
            'answers': {},
            'candidateName': 'Student One',
            'accessKey': self.paper_one_access_key
        }).get_json()

        send_eapcet_solution_email('student@example.com', result_payload)

        smtp_instance = smtp_mock.return_value.__enter__.return_value
        smtp_instance.login.assert_called_once_with('sender@example.com', 'abcdefghijklmnop')

    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_SENDER_PASSWORD': 'wrongpassword'
    }, clear=False)
    @patch('app.smtplib.SMTP')
    def test_email_endpoint_returns_actionable_auth_error(self, smtp_mock):
        smtp_instance = smtp_mock.return_value.__enter__.return_value
        smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b'5.7.8 Authentication failed')

        response = self.client.post('/eapcet/papers/1/email-solution', json={
            'email': 'student@example.com',
            'answers': {},
            'candidateName': 'Student One',
            'accessKey': self.paper_one_access_key
        })

        self.assertEqual(response.status_code, 502)
        payload = response.get_json()
        self.assertIn('SMTP authentication failed', payload['error'])


if __name__ == '__main__':
    unittest.main()
