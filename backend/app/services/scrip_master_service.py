
import os
import pandas as pd
import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ScripMasterService:
    """Service to manage 5paisa scrip master and resolution"""
    
    SCRIP_MASTER_FILE = "5paisa_scrip_master.csv"
    DOWNLOAD_URL = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
    
    _cache: Optional[pd.DataFrame] = None

    # Hardcoded fallback map for common stocks to avoid download dependency
    COMMON_SCRIPS = {
        "SBIN": 3045,
        "RELIANCE": 2885,
        "TATASTEEL": 3499,
        "INFY": 1594,
        "HDFCBANK": 1333,
        "ICICIBANK": 4963,
        "AXISBANK": 5900,
        "KOTAKBANK": 1922,
        "ITC": 1660,
        "LICI": 1515,
        "TCS": 11536,
        "LT": 11483,
        "BHARTIARTL": 10604,
        "MARUTI": 10999,
        "SUNPHARMA": 3351,
        "ULTRACEMCO": 11532,
        "POWERGRID": 14977,
        "NTPC": 11630,
        "TITAN": 3506,
        "BAJFINANCE": 317,
        "WIPRO": 3787,
        "ADANIENT": 25,
        "ADANIGREEN": 556,
        "ADANIPORTS": 15083,
        "HNDFDS": 1330,
        "BAJAJFINSV": 16675,
        "PNB": 10666,
        "BANKBARODA": 4668,
        "CANBK": 10794,
        "TATAMOTORS": 3456
    }

    @classmethod
    def _load_master(cls) -> pd.DataFrame:
        """Load scrip master from file"""
        
        if os.path.exists(cls.SCRIP_MASTER_FILE) and os.path.getsize(cls.SCRIP_MASTER_FILE) > 0:
            try:
                if cls._cache is None:
                    cls._cache = pd.read_csv(cls.SCRIP_MASTER_FILE)
                return cls._cache
            except Exception as e:
                logger.error(f"Error loading scrip master: {e}")
        
        return pd.DataFrame()

    @classmethod
    def download_scrip_master(cls):
        """Download fresh scrip master from 5paisa - DISABLED AUTO RUN"""
        # User requested to disable this to prevent errors
        logger.warning("Scrip master download is currently DISABLED to prevent startup errors.")
        return

    @classmethod
    def get_scrip_code(cls, symbol: str, exchange: str = "NSE") -> Optional[int]:
        """
        Lookup scrip code for a given symbol and exchange
        """
        # 1. Check Hardcoded Map First (Fastest, no crash)
        if exchange.upper() == "NSE" and symbol.upper() in cls.COMMON_SCRIPS:
            return cls.COMMON_SCRIPS[symbol.upper()]

        # 2. Try Cache/File
        master = cls._load_master()
        if master.empty:
            logger.warning(f"Scrip code not found in hardcoded list and master file missing: {symbol}")
            return None
            
        # 5paisa exch mapping: 'N' for NSE, 'B' for BSE
        paisa_exch = 'N' if exchange.upper() == "NSE" else 'B'
        
        # Filter by symbol and exchange
        result = master[
            (master['ShortName'].str.upper() == symbol.upper()) & 
            (master['Exch'] == paisa_exch)
        ]
        
        if result.empty:
            result = master[
                (master['Name'].str.upper() == symbol.upper()) & 
                (master['Exch'] == paisa_exch)
            ]
            
        if not result.empty:
            return int(result.iloc[0]['Scripcode'])
            
        logger.warning(f"ScripCode not found for {symbol} on {exchange}")
        return None

    @classmethod
    def clear_cache(cls):
        """Force reload from disk next time"""
        cls._cache = None
