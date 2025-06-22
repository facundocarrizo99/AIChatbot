import unittest
from unittest.mock import patch, MagicMock
import os
from datetime import datetime, timezone
from pathlib import Path

from ..services.arca_service import ARCAService
from ..arca.authentication import AFIPCredentials
from ..arca.electronic_invoice import ElectronicInvoice
from ..arca.journal import AFIPJournal

class TestARCAService(unittest.TestCase):
    def setUp(self):
        # Set up environment variables for testing
        os.environ['ARCA_CUIT'] = '20267565393'
        os.environ['ARCA_URL'] = 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL'
        
        # Create test certificates directory and dummy files
        self.cert_path = Path("./docs/certificates")
        self.cert_path.mkdir(parents=True, exist_ok=True)
        (self.cert_path / "private_key.key").touch()
        (self.cert_path / "certificadoDN.crt").touch()
        
        self.service = ARCAService()
        
        # Sample invoice data for testing
        self.invoice_data = {
            'total_amount': 1000.0,
            'total_net': 826.45,
            'total_vat': 173.55,
            'concept': '1'
        }
        
        # Sample auth data for testing
        self.auth_data = {
            'token': 'test_token',
            'sign': 'test_sign'
        }

    def tearDown(self):
        # Clean up test files
        for file in self.cert_path.glob("*"):
            file.unlink()
        self.cert_path.rmdir()

    @patch('app.arca.journal.AFIPJournal.test_connection')
    @patch('app.arca.authentication.AFIPCredentials.authenticate')
    def test_authenticate_success(self, mock_auth, mock_test_conn):
        # Configure mocks
        mock_test_conn.return_value = True
        mock_auth.return_value = self.auth_data
        
        # Test authentication
        result = self.service.authenticate()
        
        # Verify results
        self.assertIsNotNone(result)
        self.assertEqual(result['token'], 'test_token')
        self.assertEqual(result['sign'], 'test_sign')
        
        # Verify mocks were called
        mock_test_conn.assert_called_once()
        mock_auth.assert_called_once_with('wsfe')

    @patch('app.arca.journal.AFIPJournal.test_connection')
    def test_authenticate_connection_failure(self, mock_test_conn):
        # Configure mock to simulate connection failure
        mock_test_conn.return_value = False
        
        # Test authentication
        result = self.service.authenticate()
        
        # Verify results
        self.assertIsNone(result)
        mock_test_conn.assert_called_once()

    @patch('app.services.arca_service.ARCAService.authenticate')
    @patch('app.arca.journal.AFIPJournal.get_last_invoice_number')
    @patch('app.arca.electronic_invoice.ElectronicInvoice.request_cae')
    def test_get_cae_success(self, mock_request_cae, mock_last_number, mock_auth):
        # Configure mocks
        mock_auth.return_value = self.auth_data
        mock_last_number.return_value = 42
        mock_request_cae.return_value = True
        
        # Test CAE request
        result = self.service.get_cae(self.invoice_data)
        
        # Verify results
        self.assertIn('invoice_number', result)
        self.assertIn('cae', result)
        self.assertIn('cae_due_date', result)
        
        # Verify mocks were called
        mock_auth.assert_called_once()
        mock_last_number.assert_called_once()
        mock_request_cae.assert_called_once()

    @patch('app.services.arca_service.ARCAService.authenticate')
    def test_get_cae_auth_failure(self, mock_auth):
        # Configure mock to simulate authentication failure
        mock_auth.return_value = None
        
        # Test CAE request
        result = self.service.get_cae(self.invoice_data)
        
        # Verify results
        self.assertIn('error', result)
        self.assertIsNone(result['cae'])
        self.assertIsNone(result['cae_due_date'])

    def test_legacy_invoice_format(self):
        # Create a mock invoice object that matches the legacy format
        class MockInvoice:
            def __init__(self):
                self.total = 1000.0
                self.neto = 826.45
                self.iva = 173.55
                self.cae = None
                self.fecha_vencimiento_cae = None
        
        mock_invoice = MockInvoice()
        
        # Test legacy method with fallback
        result = self.service.agregar_cae(mock_invoice)
        
        # Verify results
        self.assertIsNotNone(result.cae)
        self.assertIsNotNone(result.fecha_vencimiento_cae)
        self.assertTrue(len(result.cae) == 14)  # CAE should be 14 digits

    def test_fecha_vencimiento_format(self):
        # Test date format
        result = self.service.generar_fecha_vencimiento_iso8601()
        
        # Verify ISO8601 format
        try:
            datetime.strptime(result, "%Y-%m-%dT%H:%M:%SZ")
            is_valid_date = True
        except ValueError:
            is_valid_date = False
        
        self.assertTrue(is_valid_date)

if __name__ == '__main__':
    unittest.main() 