import random
import logging
from datetime import datetime, timedelta, timezone

from typing import Dict, Optional
from app.services.arca_auth_service import AFIPAuthService
from app.config.arca_config import AFIPConfig

logger = logging.getLogger(__name__)

class InvoiceService:
    def __init__(self):
        self.auth_service = AFIPAuthService()
        self.config = AFIPConfig()
        self.wsfe = None

    def _get_wsfe(self):
        """Lazy import of WSFEv1 to avoid hard dependency on pyafipws at startup."""
        if self.wsfe is None:
            from pyafipws.wsfev1 import WSFEv1
            self.wsfe = WSFEv1()
        return self.wsfe

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
            wsfe = self._get_wsfe()
            wsfe.Conectar(wsdl=self.config.WSFE_URL + "?WSDL",
                               cache=None,
                               wrapper="WSFEv1",
                               proxy=None,
                               cacert=None)

            # Set credentials
            wsfe.SetTicketAcceso(auth['token'], auth['sign'])

            # Set invoice data
            tipo_cbte = invoice_data.get('tipo_cbte', 1)  # 1: Factura A, 6: Factura B
            punto_vta = invoice_data.get('punto_vta', 1)
            cbte_nro = invoice_data.get('cbte_nro')
            imp_total = str(invoice_data.get('importe_total', 0))

            # Request CAE
            cae = wsfe.Authorize(tipo_cbte, punto_vta, cbte_nro,
                                  imp_total, imp_total, imp_total,
                                  imp_total, imp_total, imp_total,
                                  imp_total, imp_total, imp_total)

            if wsfe.Excepcion:
                return {
                    'error': f"AFIP Exception: {wsfe.Excepcion}",
                    'success': False
                }

            if not cae:
                return {
                    'error': f"Failed to get CAE: {wsfe.ErrMsg}",
                    'success': False
                }

            return {
                'success': True,
                'cae': cae,
                'cae_expiration': wsfe.Vencimiento,
                'invoice_number': wsfe.CbteNro,
                'result': wsfe.Resultado,
                'observations': wsfe.Obs
            }

        except Exception as e:
            logger.error(f"Error requesting CAE: {str(e)}")
            return {
                'error': f"Error processing request: {str(e)}",
                'success': False
            }

class ARCAService:
    def __init__(self):
        pass  # No need to store random module as instance variable

    def agregar_cae(self, una_factura):
        una_factura.cae = str(random.randint(10 ** 13, 10 ** 14 - 1))
        una_factura.fecha_vencimiento_cae = self.generar_fecha_vencimiento_iso8601()
        return una_factura

    def generar_fecha_vencimiento_iso8601(self):
        fecha_vencimiento = datetime.now(timezone.utc) + timedelta(days=10)
        return fecha_vencimiento.strftime("%Y-%m-%dT%H:%M:%SZ")
