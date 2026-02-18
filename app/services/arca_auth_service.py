# app/services/afip_auth_service.py
import os
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.config.arca_config import AFIPConfig

logger = logging.getLogger(__name__)


class AFIPAuthService:
    def __init__(self):
        self.wsaa = None
        self.config = AFIPConfig()
        self.cache = {}

    def _get_wsaa(self):
        """Lazy import of WSAA to avoid hard dependency on pyafipws at startup."""
        if self.wsaa is None:
            from pyafipws.wsaa import WSAA
            self.wsaa = WSAA()
        return self.wsaa

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
            wsaa = self._get_wsaa()
            tra = wsaa.CreateTRA(service=service)
            cms = wsaa.SignTRA(tra, cert, private_key)

            # Request authorization
            response = wsaa.Conectar(wsdl=wsdl, cache=None, proxy=None, wrapper=None, cacert=None,
                                     url=self.config.WSAA_URL, cache_dir=self.config.CACHE_DIR)

            if not response:
                logger.error("Failed to connect to WSAA")
                return None

            # Get token and sign
            token = wsaa.Token
            sign = wsaa.Sign
            expiration = wsaa.expirationTime

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