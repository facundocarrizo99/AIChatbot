
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List

# Constants for invoice types
INVOICE_TYPES = [
    ('1', '01-Factura A'),
    ('2', '02-Nota de Débito A'),
    ('3', '03-Nota de Crédito A'),
    ('4', '04-Recibos A'),
    ('5', '05-Nota de Venta al Contado A'),
    ('6', '06-Factura B'),
    ('7', '07-Nota de Débito B'),
    ('8', '08-Nota de Crédito B'),
    ('9', '09-Recibos B'),
    ('10', '10-Notas de Venta al Contado B'),
    ('11', '11-Factura C'),
    ('12', '12-Nota de Débito C'),
    ('13', '13-Nota de Crédito C'),
    ('15', 'Recibo C'),
    ('19', '19-Factura E'),
    ('20', '20-Nota de Débito E'),
    ('21', '21-Nota de Crédito E'),
]

@dataclass
class AFIPJournal:
    """Modern implementation of AFIP Journal configuration"""
    company_cuit: str
    point_of_sale: int
    invoice_type: str
    service: str = 'wsfe'  # Default to internal market
    errors: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)

    def test_connection(self) -> bool:
        """Test AFIP webservices connection"""
        try:
            # Import AFIP webservice helper
            if self.service == "wsfe":
                from pyafipws.wsfev1 import WSFEv1
                ws = WSFEv1()
            elif self.service == "wsfex":
                from pyafipws.wsfexv1 import WSFEXv1
                ws = WSFEXv1()
            elif self.service == "wsmtxca":
                from pyafipws.wsmtx import WSMTXCA
                ws = WSMTXCA()
            else:
                raise ValueError(f"Service {self.service} not supported")

            # Connect and test
            ws.Conectar()
            ws.Dummy()
            
            msg = (f"AFIP service {self.service} - "
                  f"AppServer: {ws.AppServerStatus}, "
                  f"DbServer: {ws.DbServerStatus}, "
                  f"AuthServer: {ws.AuthServerStatus}")
            
            self.messages.append(msg)
            return True

        except Exception as e:
            self.errors.append(str(e))
            logging.error(f"AFIP Connection error: {e}")
            return False

    def get_points_of_sale(self, auth_data: Dict) -> List[str]:
        """Get enabled points of sale from AFIP"""
        try:
            from pyafipws.wsfev1 import WSFEv1
            ws = WSFEv1()
            
            # Connect and authenticate
            ws.Conectar()
            ws.Token = auth_data['token']
            ws.Sign = auth_data['sign']
            ws.Cuit = self.company_cuit

            # Get points of sale
            points = ws.ParamGetPtosVenta(sep=" ")
            return points

        except Exception as e:
            self.errors.append(str(e))
            logging.error(f"Error getting points of sale: {e}")
            return []

    def get_last_invoice_number(self, auth_data: Dict) -> Optional[int]:
        """Get last invoice number from AFIP"""
        try:
            if self.service == "wsfe":
                from pyafipws.wsfev1 import WSFEv1
                ws = WSFEv1()
            elif self.service == "wsfex":
                from pyafipws.wsfexv1 import WSFEXv1
                ws = WSFEXv1()
            elif self.service == "wsmtxca":
                from pyafipws.wsmtx import WSMTXCA
                ws = WSMTXCA()
            else:
                raise ValueError(f"Service {self.service} not supported")

            # Connect and authenticate
            ws.Conectar()
            ws.Token = auth_data['token']
            ws.Sign = auth_data['sign']
            ws.Cuit = self.company_cuit

            # Get last invoice number
            if self.service in ("wsfe", "wsmtxca"):
                last_number = ws.CompUltimoAutorizado(self.invoice_type, self.point_of_sale)
            else:
                last_number = ws.GetLastCMP(self.invoice_type, self.point_of_sale)

            return int(last_number)

        except Exception as e:
            self.errors.append(str(e))
            logging.error(f"Error getting last invoice number: {e}")
            return None


    