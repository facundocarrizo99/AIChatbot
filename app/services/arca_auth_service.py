# app/services/afip_auth_service.py
import os
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from pyafipws.wsaa import WSAA
from app.config.arca_config import AFIPConfig

logger = logging.getLogger(__name__)


class AFIPAuthService:
    def __init__(self):
        self.wsaa = WSAA()
        self.config = AFIPConfig()
        self.cache = {}

    def authenticate(self, service: str = 'wsfe') -> Optional[Dict[str, str]]:
        """
        Authenticate with AFIP WSAA and return token and sign

        Args:
            service: AFIP service to authenticate with (default: 'wsfe')

        Returns:
            Dict containing 'token', 'sign' and 'expiration' or None if authentication fails
        """
        try:
            # Check if we have a valid token in cache
            cache_key = f"{service}_auth"
            cached_auth = self.cache.get(cache_key)

            if cached_auth and cached_auth.get('expiration') > datetime.now():
                return cached_auth

            # Authenticate with WSAA
            cert = self.config.CERT_FILE
            private_key = self.config.PRIVATE_KEY_FILE
            wsdl = self.config.WSAA_URL + "?wsdl"

            # Create ticket request
            tra = self.wsaa.CreateTRA(service=service)
            cms = self.wsaa.SignTRA(tra, cert, private_key)

            # Request authorization
            response = self.wsaa.Conectar(wsdl=wsdl, cache=None, proxy=None, wrapper=None, cacert=None,
                                          url=self.config.WSAA_URL, cache_dir=self.config.CACHE_DIR)

            if not response:
                logger.error("Failed to connect to WSAA")
                return None

            # Get token and sign
            token = self.wsaa.Token
            sign = self.wsaa.Sign
            expiration = self.wsaa.expirationTime

            if not token or not sign:
                logger.error("Failed to get token and sign from WSAA")
                return None

            # Cache the credentials
            auth_data = {
                'token': token,
                'sign': sign,
                'expiration': expiration
            }
            self.cache[cache_key] = auth_data

            return auth_data

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None