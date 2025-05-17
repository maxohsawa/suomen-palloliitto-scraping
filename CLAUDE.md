# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraping project for extracting administrator contact information from a Finnish youth soccer league website. The specific flow and requirements will be determined based on the target website structure.

## Commands

### Setup
- Create virtual environment: `python3 -m venv .venv`
- Activate virtual environment (macOS/Linux): `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Development
- Run the scraper: `python src/main.py`
- Run tests: `pytest` (once tests are added)

## Architecture

The project structure will be organized as follows:
- `src/` - Main source code directory
  - `main.py` - Entry point for the scraper
- `tests/` - Test directory
- `data/` - Output data directory (gitignored)
- `requirements.txt` - Python dependencies

## Important Notes

- Target website: Finnish youth soccer league
- Specific scraping flow to be determined based on website structure
- Output data will be saved in the `data/` directory which is gitignored
- Package selection will be based on specific scraping requirements
