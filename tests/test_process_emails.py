import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy import Column, String, DateTime
from process_emails import modify_gmail_messages, build_condition_expression


class MockEmail:
    """Mock class to simulate the Email model."""

    subject = Column(String)
    date_received = Column(DateTime)


class TestProcessEmails(unittest.TestCase):
    @patch("process_emails.get_gmail_service")
    def test_modify_gmail_messages_success(self, mock_get_gmail_service):
        # Mock Gmail service
        mock_service = MagicMock()
        mock_get_gmail_service.return_value = mock_service

        # Call the function
        modify_gmail_messages(
            gmail_service=mock_service,
            message_ids=["msg1", "msg2"],
            labels_to_add=["Label_1"],
            labels_to_remove=["Label_2"],
        )

        # Assert batchModify was called with correct arguments
        mock_service.users().messages().batchModify.assert_called_once_with(
            userId="me",
            body={
                "ids": ["msg1", "msg2"],
                "addLabelIds": ["Label_1"],
                "removeLabelIds": ["Label_2"],
            },
        )

    @patch("process_emails.get_gmail_service")
    def test_modify_gmail_messages_exception(self, mock_get_gmail_service):
        # Mock Gmail service to raise an exception
        mock_service = MagicMock()
        mock_service.users().messages().batchModify.side_effect = Exception("API Error")
        mock_get_gmail_service.return_value = mock_service

        # Call the function and assert no exception is raised
        modify_gmail_messages(
            gmail_service=mock_service,
            message_ids=["msg1", "msg2"],
            labels_to_add=["Label_1"],
            labels_to_remove=["Label_2"],
        )

    def test_build_condition_expression_valid(self):
        # Use the mock Email model
        condition = {
            "field": "subject",
            "predicate": "contains",
            "value": "test",
        }
        expression = build_condition_expression(condition)
        self.assertIsNotNone(expression)

        # Test valid date condition
        condition = {
            "field": "date_received",
            "predicate": "greater_than",
            "value": "30",
            "unit": "days",
        }
        expression = build_condition_expression(condition)
        self.assertIsNotNone(expression)

    def test_build_condition_expression_invalid_field(self):
        # Test invalid field
        condition = {
            "field": "invalid_field",
            "predicate": "contains",
            "value": "test",
        }
        expression = build_condition_expression(condition)
        self.assertIsNone(expression)

    def test_build_condition_expression_missing_predicate(self):
        # Test missing predicate
        condition = {
            "field": "subject",
            "value": "test",
        }
        expression = build_condition_expression(condition)
        self.assertIsNone(expression)


if __name__ == "__main__":
    unittest.main()
