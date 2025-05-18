import unittest
from unittest.mock import MagicMock, patch
from fetch_emails import fetch_email_lists, fetch_label_lists


class TestFetchEmails(unittest.TestCase):
    @patch("fetch_emails.get_gmail_service")
    def test_fetch_label_lists_success(self, mock_get_gmail_service):
        # Mock Gmail service
        mock_service = MagicMock()
        mock_get_gmail_service.return_value = mock_service

        # Mock response for labels().list()
        mock_service.users().labels().list().execute.return_value = {
            "labels": [
                {"id": "INBOX", "name": "Inbox"},
            ]
        }

        # Call the function
        labels = fetch_label_lists(mock_service)

        # Assertions
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0]["id"], "INBOX")
        self.assertEqual(labels[0]["name"], "Inbox")

    @patch("fetch_emails.get_gmail_service")
    def test_fetch_label_lists_empty(self, mock_get_gmail_service):
        # Mock Gmail service
        mock_service = MagicMock()
        mock_get_gmail_service.return_value = mock_service

        # Mock response for labels().list()
        mock_service.users().labels().list().execute.return_value = {"labels": []}

        # Call the function
        labels = fetch_label_lists(mock_service)

        # Assertions
        self.assertEqual(len(labels), 0)

    @patch("fetch_emails.get_gmail_service")
    def test_fetch_label_lists_exception(self, mock_get_gmail_service):
        # Mock Gmail service
        mock_service = MagicMock()
        mock_get_gmail_service.return_value = mock_service

        # Mock exception for labels().list()
        mock_service.users().labels().list().execute.side_effect = Exception(
            "API Error"
        )

        # Call the function
        labels = fetch_label_lists(mock_service)

        # Assertions
        self.assertEqual(len(labels), 0)

    @patch("fetch_emails.get_gmail_service")
    def test_fetch_email_lists_success(self, mock_get_gmail_service):
        # Mock Gmail service
        mock_service = MagicMock()
        mock_get_gmail_service.return_value = mock_service

        # Mock response for messages().list()
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "123", "threadId": "456"}]
        }

        # Mock response for messages().get()
        mock_service.users().messages().get().execute.return_value = {
            "id": "123",
            "threadId": "456",
            "payload": {
                "headers": [
                    {"name": "Date", "value": "Mon, 20 Mar 2023 10:00:00 -0700"},
                    {"name": "From", "value": "abc@gmail.com"},
                    {"name": "To", "value": "xyz@gmail.com"},
                    {"name": "Subject", "value": "Test Email"},
                ]
            },
        }

        # Call the function
        emails = fetch_email_lists(mock_service)

        # Assertions
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]["id"], "123")
        self.assertEqual(emails[0]["thread_id"], "456")
        self.assertEqual(emails[0]["subject"], "Test Email")
        self.assertEqual(emails[0]["sender"], "abc@gmail.com")
        self.assertEqual(emails[0]["recepient"], "xyz@gmail.com")
        self.assertIsNotNone(emails[0]["date_received"])

    @patch("fetch_emails.get_gmail_service")
    def test_fetch_email_lists_empty(self, mock_get_gmail_service):
        # Mock Gmail service
        mock_service = MagicMock()
        mock_get_gmail_service.return_value = mock_service

        # Mock response for messages().list()
        mock_service.users().messages().list().execute.return_value = {"messages": []}

        # Call the function
        emails = fetch_email_lists(mock_service)

        # Assertions
        self.assertEqual(len(emails), 0)

    @patch("fetch_emails.get_gmail_service")
    def test_fetch_email_lists_exception(self, mock_get_gmail_service):
        # Mock Gmail service
        mock_service = MagicMock()
        mock_get_gmail_service.return_value = mock_service

        # Mock exception for messages().list()
        mock_service.users().messages().list().execute.side_effect = Exception(
            "API Error"
        )

        # Call the function
        emails = fetch_email_lists(mock_service)

        # Assertions
        self.assertEqual(len(emails), 0)


if __name__ == "__main__":
    unittest.main()
