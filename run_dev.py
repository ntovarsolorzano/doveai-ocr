#!/usr/bin/env python3
"""
Development script to run the DoveAI OCR application locally.
This script sets up and runs both the backend and frontend for development.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Error: Python 3.8 or higher is required.")
        return False
    
    # Check if pip is installed
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: pip is not installed or not working properly.")
        return False
    
    # Check if MISTRAL_API_KEY is set
    if not os.environ.get("MISTRAL_API_KEY"):
        print("Warning: MISTRAL_API_KEY environment variable is not set.")
        print("You will need to set it before running the application.")
        api_key = input("Enter your MistralAI API key (or press Enter to skip): ").strip()
        if api_key:
            os.environ["MISTRAL_API_KEY"] = api_key
        else:
            print("No API key provided. You'll need to set it manually later.")
    
    return True

def setup_backend():
    """Set up the backend environment."""
    print("\nSetting up backend...")
    backend_dir = Path("backend")
    
    # Create virtual environment if it doesn't exist
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    
    # Determine the pip and python commands based on the OS
    if sys.platform == "win32":
        pip_cmd = str(venv_dir / "Scripts" / "pip")
        python_cmd = str(venv_dir / "Scripts" / "python")
    else:
        pip_cmd = str(venv_dir / "bin" / "pip")
        python_cmd = str(venv_dir / "bin" / "python")
    
    # Install dependencies
    print("Installing backend dependencies...")
    subprocess.run([pip_cmd, "install", "-r", str(backend_dir / "requirements.txt")], check=True)
    
    return python_cmd

def run_backend(python_cmd):
    """Run the backend server."""
    print("\nStarting backend server...")
    backend_process = subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend"
    )
    return backend_process

def open_frontend():
    """Open the frontend in a web browser."""
    print("\nOpening frontend in web browser...")
    frontend_path = os.path.abspath("frontend/index.html")
    frontend_url = f"file://{frontend_path}"
    
    # Wait a moment for the backend to start
    time.sleep(2)
    
    # Open the frontend in the default web browser
    webbrowser.open(frontend_url)
    
    print(f"\nFrontend is available at: {frontend_url}")
    print("Backend API is available at: http://localhost:8000")
    print("\nNote: For API calls to work properly, you may need to adjust CORS settings or use a local server for the frontend.")

def main():
    """Main function to run the development setup."""
    print("DoveAI OCR - Development Setup")
    print("==============================")
    
    if not check_prerequisites():
        return
    
    try:
        python_cmd = setup_backend()
        backend_process = run_backend(python_cmd)
        open_frontend()
        
        print("\nPress Ctrl+C to stop the servers...")
        backend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nDevelopment server stopped.")

if __name__ == "__main__":
    main()
