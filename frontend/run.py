#!/usr/bin/env python3
"""
Run script for Codebase Genius Frontend
Handles setup and execution
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path


def check_python_version():
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 10):
        print("Error: Python 3.10 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")


def check_backend():
    """Check if backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✓ Backend is running")
            return True
        else:
            print("⚠ Backend returned status:", response.status_code)
            return False
    except Exception as e:
        print("⚠ Backend is not accessible:", str(e))
        print("  Please start backend with: jac serve main.jac")
        return False


def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False


def setup_config():
    """Setup configuration files"""
    print("\nSetting up configuration...")
    
    # Create .streamlit directory
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    # Create secrets.toml if it doesn't exist
    secrets_file = streamlit_dir / "secrets.toml"
    if not secrets_file.exists():
        secrets_file.write_text('API_BASE_URL = "http://localhost:8000"\n')
        print("✓ Created secrets.toml")
    else:
        print("✓ secrets.toml exists")
    
    return True


def run_streamlit(port=8501, debug=False):
    """Run Streamlit application"""
    print(f"\nStarting Streamlit on port {port}...")
    print("Press Ctrl+C to stop\n")
    
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.headless", "true" if not debug else "false"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nStopping Streamlit...")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run Codebase Genius Frontend")
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run Streamlit on (default: 8501)"
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip backend availability check"
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only perform setup, don't run app"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Codebase Genius - Frontend Runner")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup configuration
    if not setup_config():
        sys.exit(1)
    
    # Check backend
    if not args.skip_check:
        check_backend()
    
    if args.setup_only:
        print("\n✓ Setup complete!")
        print("\nRun the app with:")
        print(f"  python run.py")
        return
    
    # Run Streamlit
    print("\n" + "=" * 50)
    run_streamlit(port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()