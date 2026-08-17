import os
import sys
import time
import webbrowser
import uvicorn
from pathlib import Path

# Force UTF-8 output on Windows to support emoji in print statements
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
ROOT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

def main():
    print("=" * 60)
    print("  🛡️  AI Red-Teaming Demo Launcher — AstraBank Support Bot")
    print("=" * 60)
    print("\nStarting local FastAPI server at http://localhost:8000 ...")
    print("Frontend UI will be served at http://localhost:8000/app/")
    print("\nOpening web browser...")
    
    # Schedule browser opening
    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000/app/")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    from backend.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()
