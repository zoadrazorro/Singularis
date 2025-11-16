"""
Start GWM Game World Model Service

Simple wrapper to start the GWM FastAPI service.

Usage:
    python start_gwm_service.py
    python start_gwm_service.py --port 8002
"""

import os
import sys
import argparse
from loguru import logger


def main():
    parser = argparse.ArgumentParser(description="Start GWM Service")
    
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Service host')
    parser.add_argument('--port', type=int, default=8002,
                        help='Service port')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['GWM_SERVICE_HOST'] = args.host
    os.environ['GWM_SERVICE_PORT'] = str(args.port)
    
    logger.info(f"Starting GWM service on {args.host}:{args.port}")
    logger.info(f"Service will be available at http://{args.host}:{args.port}")
    logger.info("Waiting for engine snapshots...")
    
    # Import and run service
    from singularis.gwm.gwm_service import main as service_main
    service_main()


if __name__ == "__main__":
    main()
