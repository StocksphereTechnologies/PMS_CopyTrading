# need to work on this

"""
Service to fetch instruments from brokers (handles both API and file downloads)
"""
import asyncio
import requests
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import json

logger = logging.getLogger(__name__)


class InstrumentFetcher:
    """Fetches instruments from brokers"""
    
    @staticmethod
    async def fetch_5paisa_scrip_master(segment: str = "nse_eq") -> List[Dict[str, Any]]:
        """
        Fetch 5paisa scrip master directly from API
        
        Args:
            segment: Exchange segment. Valid values: all, bse_eq, nse_eq, nse_fo, bse_fo, ncd_fo, mcx_fo
                   Default: nse_eq (NSE Equity)
        
        Returns:
            List of instrument dictionaries
        """
        # Map user-friendly names to API segment names
        segment_map = {
            "NSE": "nse_eq",
            "BSE": "bse_eq", 
            "NFO": "nse_fo",
            "BFO": "bse_fo",
            "MCX": "mcx_fo",
            "NCD": "ncd_fo",
            "ALL": "all"
        }
        
        # Convert to API format if needed
        api_segment = segment_map.get(segment.upper(), segment.lower())
        
        
        if api_segment == "all":
            segments_to_try = ["all", "nse_eq", "bse_eq", "nse_fo"]
        elif api_segment == "nse_eq":
            segments_to_try = ["nse_eq", "all", "bse_eq"]
        elif api_segment == "bse_eq":
            segments_to_try = ["bse_eq", "all", "nse_eq"]
        else:
            segments_to_try = [api_segment, "all", "nse_eq", "bse_eq"]
        
        for seg in segments_to_try:
            try:
                
                url = f"https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/{seg}"
                
                logger.info(f"Trying to fetch 5paisa Scrip Master for segment: {seg}")
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.get(url, timeout=30)
                )
                
                if response.status_code == 200:
                    # Try to parse as JSON first
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'Data' in data:
                            instruments = data['Data']
                            if instruments and len(instruments) > 0:
                                logger.info(f" Successfully fetched {len(instruments)} instruments from segment {seg}")
                                return instruments
                        elif isinstance(data, list) and len(data) > 0:
                            logger.info(f" Successfully fetched {len(data)} instruments from segment {seg}")
                            return data
                    except Exception as json_err:
                        logger.debug(f"JSON parse error: {json_err}")
                    
                    # Try to parse as CSV/Excel
                    try:
                        import io
                        df = pd.read_csv(io.StringIO(response.text))
                        if not df.empty:
                            instruments = df.to_dict('records')
                            logger.info(f" Successfully fetched {len(instruments)} instruments from CSV segment {seg}")
                            return instruments
                    except Exception as csv_err:
                        logger.debug(f"CSV parse error: {csv_err}")
                    
                    logger.warning(f"Unexpected response format from 5paisa Scrip Master for segment {seg}")
                elif response.status_code == 404:
                    logger.warning(f"Segment {seg} returned 404, trying next segment...")
                    continue
                else:
                    logger.warning(f"5paisa Scrip Master API returned {response.status_code} for segment {seg}: {response.text[:200]}")
                    continue
                    
            except Exception as e:
                logger.warning(f"Error fetching 5paisa scrip master for segment {seg}: {e}")
                continue
        
        logger.error("Failed to fetch instruments from all segments")
        return []
