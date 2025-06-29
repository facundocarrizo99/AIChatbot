import random
#import subprocess
# import os
from datetime import datetime, timedelta, timezone
# from pathlib import Path
# import xml.etree.ElementTree as ET
# import logging
# from typing import Optional, Dict
#
# from ..arca.authentication import AFIPCredentials
# from ..arca.electronic_invoice import ElectronicInvoice
# from ..arca.journal import AFIPJournal

# app/services/invoice_service.py
import logging
from random import random
from typing import Dict, Optional
from pyafipws.wsfev1 import WSFEv1
from app.services.arca_auth_service import AFIPAuthService
from app.config.arca_config import AFIPConfig

logger = logging.getLogger(__name__)


class InvoiceService:
    def __init__(self):
        self.auth_service = AFIPAuthService()
        self.config = AFIPConfig()
        self.wsfe = WSFEv1()

    def request_cae(self, invoice_data: Dict) -> Dict:
        """
        Request CAE for an invoice

        Args:
            invoice_data: Dictionary containing invoice data

        Returns:
            Dict containing CAE information or error details
        """
        try:
            # Authenticate with AFIP
            auth = self.auth_service.authenticate('wsfe')
            if not auth:
                return {'error': 'Authentication failed', 'success': False}

            # Initialize WSFE client
            self.wsfe.Conectar(wsdl=self.config.WSFE_URL + "?WSDL",
                               cache=None,
                               wrapper="WSFEv1",
                               proxy=None,
                               cacert=None)

            # Set credentials
            self.wsfe.SetTicketAcceso(auth['token'], auth['sign'])

            # Set invoice data
            # Note: Adapt these fields according to your invoice_data structure
            tipo_cbte = invoice_data.get('tipo_cbte', 1)  # 1: Factura A, 6: Factura B
            punto_vta = invoice_data.get('punto_vta', 1)
            cbte_nro = invoice_data.get('cbte_nro')
            imp_total = str(invoice_data.get('importe_total', 0))

            # Request CAE
            cae = self.wsfe.Authorize(tipo_cbte, punto_vta, cbte_nro,
                                      imp_total, imp_total, imp_total,
                                      imp_total, imp_total, imp_total,
                                      imp_total, imp_total, imp_total)

            if self.wsfe.Excepcion:
                return {
                    'error': f"AFIP Exception: {self.wsfe.Excepcion}",
                    'success': False
                }

            if not cae:
                return {
                    'error': f"Failed to get CAE: {self.wsfe.ErrMsg}",
                    'success': False
                }

            return {
                'success': True,
                'cae': cae,
                'cae_expiration': self.wsfe.Vencimiento,
                'invoice_number': self.wsfe.CbteNro,
                'result': self.wsfe.Resultado,
                'observations': self.wsfe.Obs
            }

        except Exception as e:
            logger.error(f"Error requesting CAE: {str(e)}")
            return {
                'error': f"Error processing request: {str(e)}",
                'success': False
            }

class ARCAService:
    def agregar_cae(self, una_factura):
        una_factura.cae = str(random.randint(10 ** 13, 10 ** 14 - 1))
        una_factura.fecha_vencimiento_cae = self.generar_fecha_vencimiento_iso8601()
        return una_factura

    def generar_fecha_vencimiento_iso8601(self):
        fecha_vencimiento = datetime.now(timezone.utc) + timedelta(days=10)
        return fecha_vencimiento.strftime("%Y-%m-%dT%H:%M:%SZ")

"""
class ARCAService:
    def __init__(self):
        self.cert_path = Path("./docs/certificates")
        self.cert_path.mkdir(exist_ok=True)
        self.private_key = self.cert_path / "private_key.key"
        self.certificate = self.cert_path / "certificadoDN.crt"
        self.request = self.cert_path / "certificate.csr"
        self.service_id = "wsfe"
        self.company_cuit = os.getenv("ARCA_CUIT")
        # WSAA WSDL URL (homologación/testing)
        self.wsaa_wsdl = os.getenv("ARCA_URL")
        
        # Initialize AFIP credentials
        self.credentials = AFIPCredentials(
            cuit=self.company_cuit,
            certificate=str(self.certificate),
            private_key=str(self.private_key)
        )

        # Initialize journal for invoice numbering
        self.journal = AFIPJournal(
            company_cuit=self.company_cuit,
            point_of_sale=1,  # Default point of sale
            invoice_type="1",  # Default to Factura A
            service=self.service_id
        )

    def authenticate(self) -> Optional[Dict]:
        #Authenticate with AFIP using credentials
        try:
            # Test AFIP connection first
            if not self.journal.test_connection():
                raise Exception(f"AFIP Connection failed: {self.journal.errors[-1] if self.journal.errors else 'Unknown error'}")

            # Get authentication data
            auth_data = self.credentials.authenticate(self.service_id)
            if not auth_data.get('token'):
                raise Exception(f"Authentication failed: {auth_data.get('err_msg', 'Unknown error')}")

            return auth_data

        except Exception as e:
            logging.error(f"AFIP Authentication error: {e}")
            return None

    def get_cae(self, invoice_data: Dict) -> Dict:
        #Get CAE (Electronic Authorization Code) for an invoice
        try:
            # First authenticate
            auth_data = self.authenticate()
            if not auth_data:
                raise Exception("Could not authenticate with AFIP")

            # Get next invoice number
            last_number = self.journal.get_last_invoice_number(auth_data)
            next_number = f"{self.journal.point_of_sale:04d}-{(last_number + 1):08d}"

            # Create electronic invoice
            electronic_invoice = ElectronicInvoice(
                number=next_number,
                date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                company_cuit=self.company_cuit,
                concept=invoice_data.get('concept', '1'),
                invoice_type=self.journal.invoice_type,
                point_of_sale=self.journal.point_of_sale,
                service=self.service_id,
                total_amount=float(invoice_data.get('total_amount', 0)),
                total_net=float(invoice_data.get('total_net', 0)),
                total_vat=float(invoice_data.get('total_vat', 0))
            )

            # Request CAE
            if not electronic_invoice.request_cae(auth_data):
                error_msg = electronic_invoice.errors[-1] if electronic_invoice.errors else "Unknown error"
                raise Exception(f"Error requesting CAE: {error_msg}")

            return {
                'invoice_number': next_number,
                'cae': electronic_invoice.cae,
                'cae_due_date': electronic_invoice.cae_due_date,
                'result': electronic_invoice.result,
                'observations': electronic_invoice.observations
            }

        except Exception as e:
            logging.error(f"Error getting CAE: {e}")
            return {
                'error': str(e),
                'cae': None,
                'cae_due_date': None
            }

    
"""