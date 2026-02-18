import logging
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from app.models.cliente import Cliente
from app.models.monotributista import Monotributista
import os


class Producto:
    def __init__(self, nombre, precio_unitario, cantidad):
        self.nombre = nombre
        self.precio_unitario = float(precio_unitario)
        self.cantidad = float(cantidad)
        self.total = round(self.precio_unitario * self.cantidad, 2)

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "precio_unitario": self.precio_unitario,
            "cantidad": self.cantidad,
            "unidad_medida": "unidad",
            "porcentaje_bonificacion": 0.0,
            "importe_bonificacion": 0.0,
            "total": self.total
        }


class Factura:
    def __init__(self, items=None, **kwargs):
        self.punto_venta = None
        self.numero = None
        self.fecha = datetime.now().isoformat()
        self.tipo_factura = 'C'
        self.codigo_comprobante = '011'
        self.emisor = None
        self.cliente = None
        self.periodo_facturado_desde = None
        self.periodo_facturado_hasta = None
        self.fecha_vencimiento_pago = None
        self.condicion_venta = 'Contado'
        self.productos = []
        if items:
            for item in items:
                self.productos.append(Producto(**item))
        self.total = round(sum(p.total for p in self.productos), 2)
        self.cae = None
        self.fecha_vencimiento_cae = None

    def to_dict(self):
        return {
            "punto_venta": self.emisor.punto_venta,
            "numero": self.numero,
            "fecha": self.fecha,
            "tipo_factura": self.tipo_factura,
            "codigo_comprobante": self.codigo_comprobante,
            "emisor": self.emisor.to_dict_for_factura(),
            "cliente": self.cliente.to_dict(),
            "periodo_facturado_desde": self.periodo_facturado_desde,
            "periodo_facturado_hasta": self.periodo_facturado_hasta,
            "fecha_vencimiento_pago": self.fecha_vencimiento_pago,
            "condicion_venta": self.condicion_venta,
            "productos": [p.to_dict() for p in self.productos],
            "total": self.total,
            "cae": self.cae,
            "fecha_vencimiento_cae": self.fecha_vencimiento_cae
        }

    @staticmethod
    def from_dict(data):
        factura = Factura(items=data.get("productos", []))
        factura.punto_venta = data.get("punto_venta")
        factura.numero = data.get("numero")
        factura.fecha = data.get("fecha")
        factura.tipo_factura = data.get("tipo_factura")
        factura.codigo_comprobante = data.get("codigo_comprobante")
        factura.emisor = Monotributista.from_dict(data["emisor"])
        factura.cliente = Cliente.from_dict(data["cliente"])
        factura.periodo_facturado_desde = data.get("periodo_facturado_desde")
        factura.periodo_facturado_hasta = data.get("periodo_facturado_hasta")
        factura.fecha_vencimiento_pago = data.get("fecha_vencimiento_pago")
        factura.condicion_venta = data.get("condicion_venta")
        factura.cae = data.get("cae")
        factura.fecha_vencimiento_cae = data.get("fecha_vencimiento_cae")
        return factura

    def completar_factura(self, monotributista, cliente, productos):
        self.emisor = monotributista
        self.cliente = cliente
        self.productos = [Producto(**p) for p in productos]
        self.total = sum(p.total for p in self.productos)

        # Default dates if not provided
        current_date_str = datetime.now().strftime('%Y-%m-%d')
        if not self.fecha_vencimiento_pago:
            self.fecha_vencimiento_pago = current_date_str
        if not self.periodo_facturado_desde:
            self.periodo_facturado_desde = current_date_str
        if not self.periodo_facturado_hasta:
            self.periodo_facturado_hasta = current_date_str

        return self

    @staticmethod
    def razon_smart_cut(text, max_length):
        """Smartly cut text to max_length, adding ellipsis if needed."""
        if not text:
            return ""
        text = str(text)
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        return text

    def _draw_issuer_box(self, c, y_start):
        c.saveState()
        c.roundRect(15 * mm, y_start - 35 * mm, 85 * mm, 32 * mm, 2 * mm)

        # Issuer data with proper defaults
        emisor_data = self.emisor.to_dict_for_factura() if hasattr(self, 'emisor') and self.emisor else {}
        razon_social = str(emisor_data.get('razonSocial', 'N/A') or 'N/A')
        domicilio = str(emisor_data.get('domicilio', 'N/A') or 'N/A')
        condicion_iva = str(emisor_data.get('condicionIva', 'N/A') or 'N/A')
        cuit = str(emisor_data.get('cuit', 'N/A') or 'N/A')
        ing_brutos = str(emisor_data.get('ingresosBrutos', cuit) or cuit)
        inicio_act = str(emisor_data.get('fechaInicioActividades', 'N/A') or 'N/A')

        # Draw the text with proper error handling
        try:
            c.setFont('Helvetica-Bold', 10)
            c.drawString(20 * mm, y_start - 8 * mm, "Razón Social:")
            c.setFont('Helvetica', 10)
            c.drawString(50 * mm, y_start - 8 * mm, self.razon_smart_cut(razon_social, 30))  # Add max length

            c.setFont('Helvetica-Bold', 10)
            c.drawString(20 * mm, y_start - 14 * mm, "Domicilio Comercial:")
            c.setFont('Helvetica', 8)
            c.drawString(20 * mm, y_start - 18 * mm, self.razon_smart_cut(domicilio, 50))  # Add max length

            c.setFont('Helvetica-Bold', 10)
            c.drawString(20 * mm, y_start - 24 * mm, "Condición frente al IVA:")
            c.setFont('Helvetica', 10)
            c.drawString(60 * mm, y_start - 24 * mm, self.razon_smart_cut(condicion_iva, 20))  # Add max length

        except Exception as e:
            logging.error(f"Error drawing issuer box: {e}")
            # Draw error message
            c.setFont('Helvetica', 8)
            c.drawString(20 * mm, y_start - 10 * mm, f"Error: {str(e)[:50]}...")

        c.restoreState()
        return y_start - 40 * mm

    def _draw_invoice_box(self, c, y_start):
        c.saveState()
        c.roundRect(110 * mm, y_start - 35 * mm, 85 * mm, 32 * mm, 2 * mm)

        # Invoice main details
        c.setFont('Helvetica-Bold', 20)
        c.drawCentredString(152.5 * mm, y_start - 10 * mm, "FACTURA")

        c.setFont('Helvetica-Bold', 10)
        c.drawString(115 * mm, y_start - 20 * mm, f"Punto de Venta: {self.punto_venta:05d}")
        c.drawString(155 * mm, y_start - 20 * mm, f"Comp. Nro: {self.numero:08d}")

        fecha_emision = datetime.fromisoformat(self.fecha).strftime('%d/%m/%Y')
        c.drawString(115 * mm, y_start - 26 * mm, f"Fecha de Emisión: {fecha_emision}")

        c.setFont('Helvetica-Bold', 30)
        c.drawCentredString(100 * mm, y_start - 12 * mm, self.tipo_factura)
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(100 * mm, y_start - 16 * mm, f"COD. {self.codigo_comprobante}")

        c.restoreState()

    def _draw_detail_boxes(self, c, y_start):
        c.saveState()

        # Emitter CUIT etc.
        emisor_data = self.emisor.to_dict_for_factura()
        cuit = emisor_data.get('cuit', 'N/A')
        ing_brutos = emisor_data.get('ingresosBrutos', cuit)
        inicio_act = emisor_data.get('fechaInicioActividades', 'N/A')

        c.setFont('Helvetica-Bold', 10)
        c.drawString(20 * mm, y_start, f"CUIT: {cuit}")
        c.drawString(20 * mm, y_start - 5 * mm, f"Ingresos Brutos: {ing_brutos}")
        c.drawString(20 * mm, y_start - 10 * mm, f"Fecha de Inicio de Actividades: {inicio_act}")

        # Client details box
        y_client_box = y_start - 15 * mm
        c.roundRect(15 * mm, y_client_box - 22 * mm, 180 * mm, 20 * mm, 2 * mm)

        cliente_data = self.cliente.to_dict()
        nombre_cliente = cliente_data.get('nombreCompleto', 'N/A')
        cuit_cliente = cliente_data.get('cuit', '')
        dni_cliente = cliente_data.get('dni', 'N/A')
        condicion_iva_cliente = cliente_data.get('condicionIva', 'Consumidor Final')
        domicilio_cliente = cliente_data.get('domicilio', '')

        id_label = "CUIT" if len(cuit_cliente) > 0 else "DNI"
        id_value = cuit_cliente if len(cuit_cliente) > 0 else dni_cliente

        c.setFont('Helvetica-Bold', 9)
        c.drawString(20 * mm, y_client_box - 5 * mm, "Apellido y Nombre / Razón Social:")
        c.drawString(20 * mm, y_client_box - 10 * mm, f"{id_label}:")
        c.drawString(20 * mm, y_client_box - 15 * mm, "Condición frente al IVA:")

        c.setFont('Helvetica', 9)
        c.drawString(75 * mm, y_client_box - 5 * mm, nombre_cliente)
        c.drawString(32 * mm, y_client_box - 10 * mm, id_value)
        c.drawString(65 * mm, y_client_box - 15 * mm, condicion_iva_cliente)

        # Invoice period and due date
        periodo_desde = datetime.fromisoformat(self.periodo_facturado_desde).strftime('%d/%m/%Y')
        periodo_hasta = datetime.fromisoformat(self.periodo_facturado_hasta).strftime('%d/%m/%Y')
        vencimiento_pago = datetime.fromisoformat(self.fecha_vencimiento_pago).strftime('%d/%m/%Y')

        c.setFont('Helvetica-Bold', 9)
        c.drawString(20 * mm, y_client_box - 28 * mm, "Período Facturado Desde:")
        c.drawString(90 * mm, y_client_box - 28 * mm, "Hasta:")
        c.drawString(130 * mm, y_client_box - 28 * mm, "Fecha de Vto. para el pago:")

        c.setFont('Helvetica', 9)
        c.drawString(60 * mm, y_client_box - 28 * mm, periodo_desde)
        c.drawString(102 * mm, y_client_box - 28 * mm, periodo_hasta)
        c.drawString(175 * mm, y_client_box - 28 * mm, vencimiento_pago)

        c.restoreState()
        return y_client_box - 35 * mm

    def _draw_products_table(self, c, y_start):
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors

        # Table Header
        header = ["Código", "Producto / Servicio", "Cantidad", "U. Medida", "Precio Unit.", "% Bonif", "Imp. Bonif.",
                  "Subtotal"]

        # Table Data with safe attribute access
        data = [header]
        for prod in self.productos:
            # Safely get all product attributes with defaults
            nombre = getattr(prod, 'nombre', 'Producto sin nombre')
            cantidad = getattr(prod, 'cantidad', 0)
            unidad_medida = getattr(prod, 'unidad_medida', 'unidad')  # Default to 'unidad' if not set
            precio_unitario = getattr(prod, 'precio_unitario', 0)
            porcentaje_bonif = getattr(prod, 'porcentaje_bonificacion', 0)
            importe_bonif = getattr(prod, 'importe_bonificacion', 0)
            total = getattr(prod, 'total', 0)

            row = [
                '',  # Código is empty
                str(nombre),
                f"{float(cantidad):,.2f}",
                str(unidad_medida),
                f"{float(precio_unitario):,.2f}",
                f"{float(porcentaje_bonif):,.2f}%" if float(porcentaje_bonif) > 0 else "0.00%",
                f"{float(importe_bonif):,.2f}",
                f"{float(total):,.2f}"
            ]
            data.append(row)

        # Calculate column widths (adjust as needed)
        col_widths = [20 * mm, 65 * mm, 18 * mm, 18 * mm, 22 * mm, 15 * mm, 18 * mm, 22 * mm]

        # Create and style the table
        table = Table(data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Align product name to left
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Align numbers to right
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ])

        # Draw the table
        table.setStyle(style)
        table.wrapOn(c, 15 * mm, 0)
        table_height = table._height
        table.drawOn(c, 15 * mm, y_start - table_height)

        return y_start - table_height - 5 * mm

    def _draw_footer(self, c, y_start):
        c.saveState()

        # Totals
        subtotal_str = f"$ {self.total:,.2f}"

        c.setFont('Helvetica-Bold', 10)
        c.drawRightString(195 * mm, y_start, "Subtotal:")
        c.drawRightString(195 * mm, y_start - 5 * mm, "Importe Otros Tributos:")
        c.drawRightString(195 * mm, y_start - 10 * mm, "Importe Total:")

        c.setFont('Helvetica', 10)
        c.drawRightString(180 * mm, y_start, "$ 0,00")  # Assuming no other tributes
        c.drawRightString(180 * mm, y_start - 5 * mm, "$ 0,00")
        c.drawRightString(180 * mm, y_start - 10 * mm, subtotal_str)

        # CAE information
        y_cae = y_start - 25 * mm
        c.roundRect(15 * mm, y_cae - 12 * mm, 180 * mm, 10 * mm, 2 * mm)

        # --- CORRECTED BLOCK ---
        cae_vto_date = 'N/A'
        if self.fecha_vencimiento_cae:
            # Replace 'Z' with '+00:00' for compatibility
            compatible_iso_date = self.fecha_vencimiento_cae.replace('Z', '+00:00')
            cae_vto_date = datetime.fromisoformat(compatible_iso_date).strftime('%d/%m/%Y')
        # --- END CORRECTED BLOCK ---

        c.setFont('Helvetica-Bold', 10)
        c.drawString(20 * mm, y_cae - 8 * mm, f"CAE N°: {self.cae}")
        c.drawString(120 * mm, y_cae - 8 * mm, f"Fecha de Vto. de CAE: {cae_vto_date}")
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(105 * mm, y_start, "Comprobante Autorizado")

        c.setFont('Helvetica', 8)
        c.drawCentredString(105 * mm, 15 * mm, "Pág. 1/1")

        c.restoreState()

    def factura_to_pdf(self) -> tuple[str, str]:
        """
        Generates a PDF from the invoice using ReportLab and returns the path to the generated file.

        Returns:
            tuple[str, str]: Tuple containing (absolute_path, filename) of the generated PDF
        """
        try:
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)

            logger.info("Starting PDF generation")

            # Configurar rutas
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
            invoices_dir = os.path.join(base_dir, 'docs', 'invoice')
            os.makedirs(invoices_dir, exist_ok=True)

            # Crear nombre de archivo con formato: CUIT_CODIGO_PV_NRO.pdf
            cuit_emisor = str(self.emisor.cuit).replace('-', '')
            pdf_filename = f"{cuit_emisor}_{self.codigo_comprobante}_{self.punto_venta:05d}_{self.numero:08d}.pdf"
            pdf_path = os.path.join(invoices_dir, pdf_filename)

            # Crear el documento PDF
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4  # width=595.27, height=841.89

            # Draw sections
            y_pos = self._draw_issuer_box(c, height - 15 * mm)
            self._draw_invoice_box(c, height - 15 * mm)
            y_pos = self._draw_detail_boxes(c, y_pos)
            y_pos = self._draw_products_table(c, y_pos)
            self._draw_footer(c, y_pos)

            # Save the PDF
            c.save()

            logger.info(f"PDF successfully generated at: {pdf_path}")
            return (os.path.abspath(pdf_path), pdf_filename)

        except Exception as e:
            logger.error(f"Error al generar PDF: {e}", exc_info=True)
            raise