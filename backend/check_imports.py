
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    print("Checking app.main import...")
    from app.main import app
    print("Successfully imported app.main:app")
    
    print("Checking ZerodhaAdapter import...")
    from app.adapters.zerodha_adapter import ZerodhaAdapter
    print("Successfully imported ZerodhaAdapter")
    
    print("Checking MarginService import...")
    from app.services.margin_service import MarginService
    print("Successfully imported MarginService")
    
    print("Checking PositionService import...")
    from app.services.position_service import PositionService
    print("Successfully imported PositionService")
    
    print("All critical imports verified successfully!")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
