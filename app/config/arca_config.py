# app/config/afip_config.py
import os
from pathlib import Path


class AFIPConfig:
    # AFIP Environment (testing or production)
    ENVIRONMENT = os.getenv('AFIP_ENVIRONMENT', 'testing')

    # Paths for certificates
    CERT_FILE = os.getenv('AFIP_CERT_FILE', 'path/to/certificate.crt')
    PRIVATE_KEY_FILE = os.getenv('AFIP_PRIVATE_KEY_FILE', 'path/to/private.key')
    CACHE_DIR = os.getenv('AFIP_CACHE_DIR', '/tmp/afip_cache')

    # Service URLs
    WSAA_URL = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms" if ENVIRONMENT == 'testing' else "https://wsaa.afip.gov.ar/ws/services/LoginCms"
    WSFE_URL = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx" if ENVIRONMENT == 'testing' else "https://servicios1.afip.gov.ar/wsfev1/service.asmx"

    # Create cache directory if it doesn't exist
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)