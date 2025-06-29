#!/usr/bin/python
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License as published by
# the Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# Copyright 2013 by Mariano Reingart
# Based on code "factura_electronica" by Luis Falcon 
# Based on code "openerp-iva-argentina" by Gerardo Allende / Daniel Blanco
# Based on code "l10n_ar_wsafip_fe" by OpenERP - Team de Localización Argentina

"Electronic Invoice for Argentina Federal Tax Administration (AFIP) webservices"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013 Mariano Reingart and others"
__license__ = "AGPL 3.0+"

import os
import time
import datetime
import decimal
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List

# AFIP country codes mapping
AFIP_COUNTRY_CODE_MAP = {
    'ar': 200, 'bo': 202, 'br': 203, 'ca': 204, 'co': 205,
    'cu': 207, 'cl': 208, 'ec': 210, 'us': 212, 'mx': 218,
    'py': 221, 'pe': 222, 'uy': 225, 've': 226, 'cn': 310,
    'tw': 313, 'in': 315, 'il': 319, 'jp': 320, 'at': 405,
    'be': 406, 'dk': 409, 'es': 410, 'fr': 412, 'gr': 413,
    'it': 417, 'nl': 423, 'pt': 620, 'uk': 426, 'sz': 430,
    'de': 438, 'ru': 444, 'eu': 497,
}

@dataclass
class ElectronicInvoice:
    """Modern implementation of AFIP Electronic Invoice"""
    number: str
    date: str
    company_cuit: str
    concept: str = '1'  # products by default
    invoice_type: Optional[str] = None
    point_of_sale: Optional[str] = None
    service: Optional[str] = None
    total_amount: float = 0.0
    total_net: float = 0.0
    total_vat: float = 0.0
    cae: Optional[str] = None
    cae_due_date: Optional[str] = None
    result: Optional[str] = None
    observations: Optional[str] = None
    errors: List[str] = field(default_factory=list)

    def request_cae(self, auth_data: Dict) -> bool:
        """Request CAE from AFIP"""
        try:
            # Import the AFIP webservice helper for electronic invoice
            if self.service == 'wsfe':
                from pyafipws.wsfev1 import WSFEv1
                ws = WSFEv1()
            elif self.service == 'wsmtxca':
                from pyafipws.wsmtx import WSMTXCA
                ws = WSMTXCA()
            elif self.service == 'wsfex':
                from pyafipws.wsfexv1 import WSFEXv1
                ws = WSFEXv1()
            else:
                raise ValueError(f"Service {self.service} not supported")

            # Connect to webservice
            ws.Conectar()
            ws.Token = auth_data['token']
            ws.Sign = auth_data['sign']
            ws.Cuit = self.company_cuit

            # Basic invoice data
            cbte_nro = int(self.number[-8:])
            ws.CrearFactura(
                concepto=self.concept,
                tipo_doc=80,  # CUIT
                nro_doc=self.company_cuit,
                tipo_cbte=self.invoice_type,
                punto_vta=self.point_of_sale,
                cbt_desde=cbte_nro,
                cbt_hasta=cbte_nro,
                imp_total=self.total_amount,
                imp_neto=self.total_net,
                imp_iva=self.total_vat
            )

            # Request authorization
            if self.service in ('wsfe', 'wsmtxca'):
                ws.CAESolicitar()
                self.cae = ws.CAE
                self.cae_due_date = ws.Vencimiento
            elif self.service == 'wsfex':
                ws.Authorize(self.number)
                self.cae = ws.CAE 
                self.cae_due_date = ws.FchVencCAE

            self.result = ws.Resultado
            self.observations = ws.Obs
            return bool(self.cae)

        except Exception as e:
            self.errors.append(str(e))
            logging.error(f"Error requesting CAE: {e}")
            return False

    def verify_number(self) -> bool:
        """Verify invoice number is valid"""
        try:
            if self.service in ('wsfe', 'wsmtxca'):
                from pyafipws.wsfev1 import WSFEv1
                ws = WSFEv1()
            elif self.service == 'wsfex':
                from pyafipws.wsfexv1 import WSFEXv1
                ws = WSFEXv1()
            else:
                raise ValueError(f"Service {self.service} not supported")

            # Get last invoice number from AFIP
            if self.service in ('wsfe', 'wsmtxca'):
                last_cbte = ws.CompUltimoAutorizado(self.invoice_type, self.point_of_sale)
            else:
                last_cbte = ws.GetLastCMP(self.invoice_type, self.point_of_sale)

            current_number = int(self.number[-8:])
            return current_number == last_cbte + 1

        except Exception as e:
            self.errors.append(str(e))
            logging.error(f"Error verifying number: {e}")
            return False

    def _get_pyafipws_barcode_img(self, cr, uid, ids, field_name, arg, context):
        "Generate the required barcode Interleaved of 7 image using PIL"
        from pyafipws.pyi25 import PyI25
        from cStringIO import StringIO as StringIO
        # create the helper:
        pyi25 = PyI25()
        images = {}
        for invoice in self.browse(cr, uid, ids):
            if not invoice.pyafipws_barcode:
                continue
            output = StringIO()
            # call the helper:
            bars = ''.join([c for c in invoice.pyafipws_barcode if c.isdigit()])
            if not bars:
                bars = "00"
            pyi25.GenerarImagen(bars, output, extension="PNG")
            # get the result and encode it for openerp binary field:
            images[invoice.id] = output.getvalue().encode("base64")
            output.close()
        return images

    # add the computed columns:
    
    _columns.update({
        'pyafipws_barcode_img': fields.function( 
            _get_pyafipws_barcode_img, type='binary', method=True, store=False),
        })


electronic_invoice()


class invoice_wizard(osv.osv_memory):
    _name = 'pyafipws.invoice.wizard'
    _columns = {
        'journal': fields.many2one('account.journal', 'Journal'),
        'cbte_nro': fields.integer('number'),
        'cae': fields.char('CAE', size=14, readonly=True, ),
        'cae_due': fields.char('Vencimiento CAE', size=10, readonly=True, ),   
        'total': fields.float('Total', readonly=True, ),
        'vat': fields.float('IVA', readonly=True, ),
    }
    def get(self,cr,uid,ids,context={}):
        #invoice = self.pool.get('account.invoice')
        for wiz in self.browse(cr, uid, ids):
            company = wiz.journal.company_id
            tipo_cbte = wiz.journal.pyafipws_invoice_type
            punto_vta = wiz.journal.pyafipws_point_of_sale
            service = wiz.journal.pyafipws_electronic_invoice_service
            # check if it is an electronic invoice sale point:
            if not tipo_cbte or not punto_vta or not service:
                raise osv.except_osv('Error !', "Solo factura electrónica")

            # authenticate against AFIP:
            auth_data = company.pyafipws_authenticate(service=service)
            # create the proxy and get the configuration system parameters:
            cfg = self.pool.get('ir.config_parameter')
            cache = cfg.get_param(cr, uid, 'pyafipws.cache', context=context)
            proxy = cfg.get_param(cr, uid, 'pyafipws.proxy', context=context)
            wsdl = cfg.get_param(cr, uid, 'pyafipws.%s.url' % service, context=context)
            
            # import the AFIP webservice helper for electronic invoice
            if service == 'wsfe':
                from pyafipws.wsfev1 import WSFEv1, SoapFault   # local market
                ws = WSFEv1()
            elif service == 'wsmtxca':
                from pyafipws.wsmtx import WSMTXCA, SoapFault   # local + detail
                wsdl = cfg.get_param(cr, uid, 'pyafipws.wsmtxca.url', context=context)
                ws = WSMTXCA()
            elif service == 'wsfex':
                from pyafipws.wsfexv1 import WSFEXv1, SoapFault # foreign trade
                wsdl = cfg.get_param(cr, uid, 'pyafipws.wsfex.url', context=context)
                ws = WSFEXv1()
            else:
                raise osv.except_osv('Error !', "%s no soportado" % service)
            
            # connect to the webservice and call to the test method
            ws.Conectar(cache or "", wsdl or "", proxy or "")
            # set AFIP webservice credentials:
            ws.Cuit = company.pyafipws_cuit
            ws.Token = auth_data['token']
            ws.Sign = auth_data['sign']

            if service in ('wsfe', 'wsmtxca'):
                if not wiz.cbte_nro:
                    wiz.cbte_nro = ws.CompUltimoAutorizado(tipo_cbte, punto_vta)
                ws.CompConsultar(tipo_cbte, punto_vta, wiz.cbte_nro)
                vat = ws.ImptoLiq
            else:
                if not wiz.cbte_nro:
                    wiz.cbte_nro = ws.GetLastCMP(tipo_cbte, punto_vta)
                ws.GetCMP(tipo_cbte, punto_vta, wiz.cbte_nro)
                vat = 0

            # update the form fields with the values returned from AFIP:
            self.write(cr, uid, ids, {'cae': ws.CAE, 'cae_due': ws.Vencimiento,
                                      'total': ws.ImpTotal or 0, 'vat': vat,
                                      'cbte_nro': ws.CbteNro,                                    
                                     }, context=context)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'pyafipws.invoice.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': wiz.id,
                'views': [(False, 'form')],
                'target': 'new',
                 }

invoice_wizard()


class report_pyfepdf(report_int):
    "Basic PDF template report for Argentina Electronic Invoices (using FPDF)"

    def create(self, cr, uid, ids, datas, context):
        import pooler
        pool = pooler.get_pool(cr.dbname)
        model_obj = pool.get("account.invoice")
        try:
            # import and instantiate the helper:
            from pyafipws.pyfepdf import FEPDF            
            fepdf = FEPDF()
            
            # load CSV default format (factura.csv)
            fepdf.CargarFormato(os.path.join(os.path.dirname(__file__), 
                                             "pyafipws", "factura.csv"))
            # set the logo image
            fepdf.AgregarDato("logo", os.path.join(os.path.dirname(__file__),
                                                   "pyafipws", "logo.png"))            
            # set amount format (decimal places):
            fepdf.FmtCantidad = "0.2"
            fepdf.FmtPrecio = "0.2"

            # TODO: complete all fields and additional data 
            for invoice in model_obj.browse(cr, uid, ids)[:1]:

                # get the electronic invoice type, point of sale and service:
                journal = invoice.journal_id
                company = journal.company_id
                tipo_cbte = journal.pyafipws_invoice_type
                punto_vta = journal.pyafipws_point_of_sale

                # set basic AFIP data:
                fepdf.CUIT = company.pyafipws_cuit

                # get the last 8 digit of the invoice number
                cbte_nro = int(invoice.number[-8:])
                cbt_desde = cbt_hasta = cbte_nro
                fecha_cbte = invoice.date_invoice
                concepto = tipo_expo = int(invoice.pyafipws_concept or 0)
                if int(concepto) != 1:
                    fecha_venc_pago = invoice.date_invoice
                    if invoice.pyafipws_billing_start_date:
                        fecha_serv_desde = invoice.pyafipws_billing_start_date
                    else:
                        fecha_serv_desde = None
                    if  invoice.pyafipws_billing_end_date:
                        fecha_serv_hasta = invoice.pyafipws_billing_end_date
                    else:
                        fecha_serv_hasta = None
                else:
                    fecha_venc_pago = fecha_serv_desde = fecha_serv_hasta = None

                # customer tax number:
                if invoice.partner_id.vat:
                    nro_doc = invoice.partner_id.vat.replace("-","")
                else:
                    nro_doc = "0"               # only "consumidor final"
                tipo_doc = 99
                if nro_doc.startswith("AR"):
                    nro_doc = nro_doc[2:]
                    if int(nro_doc)  == 0:
                        tipo_doc = 99           # consumidor final
                    elif len(nro_doc) < 11:
                        tipo_doc = 96           # DNI
                    else:
                        tipo_doc = 80           # CUIT

                # invoice amount totals:
                imp_total = str("%.2f" % abs(invoice.amount_total))
                imp_tot_conc = "0.00"
                imp_neto = str("%.2f" % abs(invoice.amount_untaxed))
                imp_iva = str("%.2f" % abs(invoice.amount_tax))
                imp_subtotal = imp_neto  # TODO: not allways the case!
                imp_trib = "0.00"
                imp_op_ex = "0.00"
                if invoice.currency_id.name == 'ARS':                
                    moneda_id = "PES"
                    moneda_ctz = 1
                else:
                    moneda_id = {'USD':'DOL'}[invoice.currency_id.name]
                    moneda_ctz = str(invoice.currency_id.rate)

                # foreign trade data: export permit, country code, etc.:
                if False: ##invoice.pyafipws_incoterms:
                    incoterms = invoice.pyafipws_incoterms.code
                    incoterms_ds = invoice.pyafipws_incoterms.name
                else:
                    incoterms = incoterms_ds = None
                if int(tipo_cbte) == 19 and tipo_expo == 1:
                    permiso_existente =  "N" or "S"     # not used now
                else:
                    permiso_existente = ""
                obs_generales = invoice.comment
                if invoice.payment_term:
                    forma_pago = invoice.payment_term.name
                    obs_comerciales = invoice.payment_term.name
                else:
                    forma_pago = obs_comerciales = None
                idioma_cbte = 1     # invoice language: spanish / español

                # customer data (foreign trade):
                nombre_cliente = invoice.partner_id.name
                if invoice.partner_id.vat:
                    if invoice.partner_id.vat.startswith("AR"):
                        # use the Argentina AFIP's global CUIT for the country:
                        cuit_pais_cliente = invoice.partner_id.vat[2:]
                        id_impositivo = None
                    else:
                        # use the VAT number directly
                        id_impositivo = invoice.partner_id.vat[2:] 
                        # TODO: the prefix could be used to map the customer country
                        cuit_pais_cliente = None
                else:
                    cuit_pais_cliente = id_impositivo = None
                # address_invoice_id -> partner_id
                if invoice.partner_id:
                    domicilio_cliente = " - ".join([
                                        invoice.partner_id.name or '',
                                        invoice.partner_id.street or '',
                                        invoice.partner_id.street2 or '',
                                        ])
                    localidad_cliente = " - ".join([
                                        invoice.partner_id.city or '',
                                        invoice.partner_id.zip or '',
                                        ])
                    provincia_cliente = invoice.partner_id.state_id
                else:
                    domicilio_cliente = ""
                    localidad_cliente = ""
                    provincia_cliente = ""
                if invoice.partner_id.country_id:
                    # map ISO country code to AFIP destination country code:
                    iso_code = invoice.partner_id.country_id.code.lower()
                    pais_dst_cmp = AFIP_COUNTRY_CODE_MAP[iso_code]                

                # set AFIP returned values 
                cae = invoice.pyafipws_cae or ""
                fch_venc_cae = (invoice.pyafipws_cae_due_date or "").replace("-", "")
                motivo = invoice.pyafipws_message or ""

                # create the invoice internally in the helper
                fepdf.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
                    cbte_nro, imp_total, imp_tot_conc, imp_neto,
                    imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
                    fecha_serv_desde, fecha_serv_hasta, 
                    moneda_id, moneda_ctz, cae, fch_venc_cae, id_impositivo,
                    nombre_cliente, domicilio_cliente, pais_dst_cmp, 
                    obs_comerciales, obs_generales, forma_pago, incoterms, 
                    idioma_cbte, motivo)
    
                # set custom extra data:
                fepdf.AgregarDato("localidad_cliente", localidad_cliente)
                fepdf.AgregarDato("provincia_cliente", provincia_cliente)

                # analyze VAT (IVA) and other taxes (tributo):
                for tax_line in invoice.tax_line:
                    if "IVA" in tax_line.name:
                        if '0%' in tax_line.name:
                            iva_id = 3
                        elif '10,5%' in tax_line.name:
                            iva_id = 4
                        elif '21%' in tax_line.name:
                            iva_id = 5
                        elif '27%' in tax_line.name:
                            iva_id = 6
                        else:
                            ivva_id = 0
                        base_imp = ("%.2f" % abs(tax_line.base))
                        importe = ("%.2f" % abs(tax_line.amount))
                        # add the vat detail in the helper
                        fepdf.AgregarIva(iva_id, base_imp, importe)
                    else:
                        if 'impuesto' in tax_line.name.lower():
                            tributo_id = 1  # nacional
                        elif 'iibbb' in tax_line.name.lower():
                            tributo_id = 3  # provincial
                        elif 'tasa' in tax_line.name.lower():
                            tributo_id = 4  # municipal
                        else:
                            tributo_id = 99
                        desc = tax_line.name
                        base_imp = ("%.2f" % abs(tax_line.base))
                        importe = ("%.2f" % abs(tax_line.amount))
                        alic = "%.2f" % tax_line.base
                        # add the other tax detail in the helper
                        fepdf.AgregarTributo(id, desc, base_imp, alic, importe)                    

                # analize line items - invoice detail
                for line in invoice.invoice_line:
                    codigo = line.product_id.code
                    u_mtx = 1                       # TODO: get it from uom? 
                    cod_mtx = line.product_id.ean13
                    ds = line.name
                    qty = line.quantity
                    umed = 7                        # TODO: line.uos_id...?
                    precio = line.price_unit
                    importe = line.price_subtotal
                    bonif = line.discount or None
                    iva_id = 5                      # TODO: line.tax_code_id?
                    imp_iva = importe * line.invoice_line_tax_id[0].amount
                    fepdf.AgregarDetalleItem(u_mtx, cod_mtx, codigo, ds, qty, umed, 
                        precio, bonif, iva_id, imp_iva, importe, despacho="")

            fepdf.CrearPlantilla(papel="A4", orientacion="portrait")
            fepdf.ProcesarPlantilla(num_copias=1, lineas_max=24, qty_pos='izq')
            report_type = datas.get('report_type', 'pdf')
            pdf = fepdf.GenerarPDF()
            return (pdf, report_type)
        except:
            # catch the exception and send a better message for the user:
            from pyafipws import utils
            ex = utils.exception_info()
            raise osv.except_osv(ex['msg'], ex['tb'])

        
report_pyfepdf('report.pyafipws.invoice')
                       