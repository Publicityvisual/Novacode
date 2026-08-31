#!/usr/bin/env python3
import sys
import os

# Add the project root to sys.path if not already there
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cli.main import main as cli_main

if __name__ == '__main__':
    cli_main()