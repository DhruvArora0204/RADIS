import os
import sys
import warnings

# Suppress third-party library deprecation and user warnings
warnings.filterwarnings("ignore")

# Ensure root workspace directory is in sys.path and env PYTHONPATH for uvicorn subprocesses
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
os.environ["PYTHONPATH"] = root_dir + os.pathsep + os.environ.get("PYTHONPATH", "")

import uvicorn

def main():
    print("=" * 60)
    print(" 🧠 RADIS Clinical AI Workstation & Backend API Server")
    print("=" * 60)
    print(" Starting FastAPI server on http://localhost:8000 ...")
    print(" Open http://localhost:8000 in your browser to access UI.")
    print("=" * 60)
    
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=root_dir)

if __name__ == "__main__":
    main()
