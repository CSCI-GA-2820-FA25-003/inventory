"""
Test Cases for Error Handlers
"""

import unittest
from unittest.mock import patch
from service.common import status
from service.models import DataValidationError
from service.common import error_handlers
from wsgi import app  # import actual Flask app to provide context


class TestErrorHandlers(unittest.TestCase):
    """Test Cases for Error Handlers"""

    def setUp(self):
        """Set up test client and push app context"""
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()  # ✅ enter Flask app context

    def tearDown(self):
        """Pop app context after tests"""
        self.app_context.pop()

    ######################################################################
    # TEST: request_validation_error
    ######################################################################
    @patch("service.common.error_handlers.bad_request")
    def test_request_validation_error(self, mock_bad_request):
        """It should call bad_request when DataValidationError occurs"""
        error = DataValidationError("Invalid data")
        error_handlers.request_validation_error(error)
        mock_bad_request.assert_called_once_with(error)

    ######################################################################
    # TEST: bad_request
    ######################################################################
    @patch("service.common.error_handlers.app.logger.warning")
    def test_bad_request(self, mock_logger):
        """It should return JSON response with 400 status"""
        error = "Bad input data"
        response, status_code = error_handlers.bad_request(error)

        mock_logger.assert_called_once_with(str(error))
        self.assertEqual(status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json["status"], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json["error"], "Bad Request")
        self.assertIn("Bad input data", response.json["message"])

    ######################################################################
    # TEST: method_not_supported
    ######################################################################
    @patch("service.common.error_handlers.app.logger.warning")
    def test_method_not_supported(self, mock_logger):
        """It should return JSON response with 405 status"""
        error = "Method not allowed for this endpoint"
        response, status_code = error_handlers.method_not_supported(error)

        mock_logger.assert_called_once_with(str(error))
        self.assertEqual(status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json["status"], status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.json["error"], "Method not Allowed")
        self.assertIn("Method not allowed", response.json["message"])

    ######################################################################
    # TEST: mediatype_not_supported
    ######################################################################
    @patch("service.common.error_handlers.app.logger.warning")
    def test_mediatype_not_supported(self, mock_logger):
        """It should return JSON response with 415 status"""
        error = "Unsupported media type: text/plain"
        response, status_code = error_handlers.mediatype_not_supported(error)

        mock_logger.assert_called_once_with(str(error))
        self.assertEqual(status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(
            response.json["status"], status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )
        self.assertEqual(response.json["error"], "Unsupported media type")
        self.assertIn("Unsupported media type", response.json["message"])

    ######################################################################
    # TEST: internal_server_error
    ######################################################################
    @patch("service.common.error_handlers.app.logger.error")
    def test_internal_server_error(self, mock_logger):
        """It should return JSON response with 500 status"""
        error = "Unexpected error occurred"
        response, status_code = error_handlers.internal_server_error(error)

        mock_logger.assert_called_once_with(str(error))
        self.assertEqual(status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json["status"], status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json["error"], "Internal Server Error")
        self.assertIn("Unexpected error occurred", response.json["message"])


if __name__ == "__main__":
    unittest.main()
