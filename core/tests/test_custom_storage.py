from datetime import UTC, datetime
from unittest.mock import patch

from django.test import TestCase, override_settings

from core.custom_storage import AzureReceiptStorage


@override_settings(
    AZURE_ACCOUNT_NAME="testaccount",
    AZURE_ACCOUNT_KEY="testkey",
    AZURE_RECEIPT_CONTAINER="testcontainer",
)
class AzureReceiptStorageTest(TestCase):
    def setUp(self):
        self.storage = AzureReceiptStorage()

    def test_get_valid_name(self):
        # Test basic filename cleaning
        self.assertEqual(
            self.storage.get_valid_name("test file.pdf"),
            "test_file.pdf"
        )

        # Test removing special characters
        self.assertEqual(
            self.storage.get_valid_name("test@#$%^&*.pdf"),
            "test.pdf"
        )

        # Test handling multiple spaces and special chars
        self.assertEqual(
            self.storage.get_valid_name("my   test   file  @#$.pdf"),
            "my___test___file__.pdf"  # Multiple underscores are preserved
        )

        # Test handling unicode characters
        self.assertEqual(
            self.storage.get_valid_name("résumé.pdf"),
            "rsum.pdf"
        )

    @patch('core.custom_storage.AzureReceiptStorage.exists')
    def test_get_available_name_no_conflict(self, mock_exists):
        # Test when file doesn't exist
        mock_exists.return_value = False
        result = self.storage.get_available_name("test.pdf")
        self.assertEqual(result, "test.pdf")

    @patch('core.custom_storage.AzureReceiptStorage.exists')
    def test_get_available_name_with_conflict(self, mock_exists):
        # Test when file exists and needs timestamp
        mock_exists.side_effect = [True, False]  # First check exists, second doesn't

        with patch('core.custom_storage.datetime') as mock_datetime:
            # Set a fixed datetime for testing
            mock_datetime.now.return_value = datetime(2025, 2, 7, 12, 30, 45, tzinfo=UTC)

            result = self.storage.get_available_name("test.pdf")
            self.assertEqual(result, "test_20250207_123045.pdf")

    @patch('core.custom_storage.AzureReceiptStorage.exists')
    def test_get_available_name_with_directory(self, mock_exists):
        # Test handling files in subdirectories
        mock_exists.return_value = False
        result = self.storage.get_available_name("receipts/2025/02/test.pdf")
        self.assertEqual(result, "receipts/2025/02/test.pdf")

    @patch('core.custom_storage.AzureReceiptStorage.exists')
    def test_get_available_name_max_length(self, mock_exists):
        # Test max length handling
        mock_exists.side_effect = [True, False]

        with patch('core.custom_storage.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 2, 7, 12, 30, 45, tzinfo=UTC)

            # Test with max_length constraint
            result = self.storage.get_available_name(
                "very_long_filename_that_exceeds_limit.pdf",
                max_length=30
            )
            self.assertTrue(len(result) <= 30)
            self.assertTrue(result.endswith('.pdf'))

    def test_init_account_key_padding(self):
        # Test key padding for base64
        with override_settings(AZURE_ACCOUNT_KEY='testkey123'):  # 9 chars
            storage = AzureReceiptStorage()
            # Base64 padding adds '=' to make length multiple of 4
            # 'testkey123' is 9 chars, so needs 2 padding chars
            self.assertEqual(storage.account_key, 'testkey123==')
