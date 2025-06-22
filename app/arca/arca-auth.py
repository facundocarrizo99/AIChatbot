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
# Copyright 2013 by
# Based on code "factura_electronica" by Luis Falcon (GPLv3)
# Based on code by "openerp-iva-argentina" by Gerardo Allende / Daniel Blanco

"Authentication functions for Argentina's Federal Tax Agency (AFIP) webservices"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013 Mariano Reingart and others"
__license__ = "AGPL 3.0"

# Están muchos valores de importe con valor absoluto, puesto que el CAE
# en AFIP no acepta valores negativos.

import os
import sys
import logging
from datetime import datetime, timedelta
from pysimplesoap.client import SoapClient

DEFAULT_TTL = 60*60*5  # five hours
WSAA_URL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"  # testing
WSAA_WSDL = f"{WSAA_URL}?wsdl"

def authenticate(service):
    """Basic AFIP WSAA authentication without certificate signing"""
    try:
        # Create SOAP client
        client = SoapClient(
            wsdl=WSAA_WSDL,
            cache=None,
            ns="web",
            soap_ns="soapenv",
            trace=True
        )

        # Get timestamp for request
        now = datetime.now()
        expiration = now + timedelta(hours=5)
        
        # Create login ticket request (TRA)
        tra = {
            'uniqueId': int(now.timestamp()),
            'generationTime': now.isoformat(),
            'expirationTime': expiration.isoformat(),
            'service': service
        }

        # Call remote method
        response = client.loginCms(in0=tra)
        
        if not response:
            raise RuntimeError("Empty response from WSAA")

        return {
            'token': response.token,
            'sign': response.sign,
            'err_msg': None
        }

    except Exception as e:
        logging.error(f"WSAA Error: {str(e)}")
        return {
            'token': None,
            'sign': None,
            'err_msg': str(e)
        }

if __name__ == '__main__':
    # Basic test
    auth_data = authenticate("wsfe")
    print(auth_data)
