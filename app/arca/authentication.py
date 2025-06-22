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
# Based on code "l10n_ar_wsafip" by OpenERP - Team de Localización Argentina

"Credentials for Argentina Federal Tax Administration (AFIP) webservices"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013 Mariano Reingart and others"
__license__ = "AGPL 3.0+"

import logging
from dataclasses import dataclass
from typing import Optional, Dict

from . import arca_auth

@dataclass
class AFIPCredentials:
    cuit: str
    certificate: str
    private_key: str
    cache: Optional[str] = None
    proxy: Optional[str] = None
    wsdl: Optional[str] = None

    def authenticate(self, service: str = "wsfe") -> Dict:
        """Authenticate against AFIP, returns token, sign, err_msg (dict)"""
        try:
            auth = arca_auth.authenticate(
                service=service,
                certificate=self.certificate,
                private_key=self.private_key,
                cache=self.cache or "",
                wsdl=self.wsdl or "",
                proxy=self.proxy or ""
            )
            return auth
        except Exception as e:
            logging.error(f"AFIP Authentication error: {str(e)}")
            return {'token': None, 'sign': None, 'err_msg': str(e)}

    def test_authentication(self, service: str = "wsfe") -> Dict:
        """Test the authentication credentials"""
        auth_data = self.authenticate(service)
        if not auth_data['token']:
            raise ValueError(f"Authentication failed: {auth_data['err_msg']}")
        return auth_data


if __name__ == "__main__":
    # Basic test
    creds = AFIPCredentials(
        cuit="20267565393",
        certificate="test.crt",
        private_key="test.key"
    )
    auth_data = creds.authenticate()
    print(auth_data)
    