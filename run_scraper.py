#!/usr/bin/env python3
"""
Entry point for running the scraper from the project root.
"""

import sys
sys.path.insert(0, '.')

from src.cli import main

if __name__ == "__main__":
    main()
