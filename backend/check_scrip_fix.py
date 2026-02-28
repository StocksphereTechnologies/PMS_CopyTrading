import sys
import os

# Ensure we can import app
sys.path.append(os.getcwd())

try:
    from app.services.scrip_master_service import ScripMasterService
    
    print("\n--- Testing ScripMasterService Fix ---")
    
    # 1. Check if COMMON_SCRIPS exists
    if hasattr(ScripMasterService, 'COMMON_SCRIPS'):
        print(f"[PASS] COMMON_SCRIPS dictionary found with {len(ScripMasterService.COMMON_SCRIPS)} entries.")
    else:
        print("[FAIL] COMMON_SCRIPS dictionary NOT found!")

    # 2. Check download method
    print(f"Download method docstring: {ScripMasterService.download_scrip_master.__doc__}")

    # 3. Test Lookup
    code = ScripMasterService.get_scrip_code("SBIN", "NSE")
    print(f"Lookup 'SBIN': {code}")
    
    if code == 3045:
        print("[PASS] Scrip lookup returned correct code 3045.")
    else:
        print(f"[FAIL] Scrip lookup returned {code} (Expected 3045).")

except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"RUNTIME ERROR: {e}")
