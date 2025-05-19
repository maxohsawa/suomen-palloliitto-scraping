# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraping project for extracting team administrator (Joukkueenjohtaja) contact information from the Finnish soccer league website (tulospalvelu.palloliitto.fi). The scraper uses a staged approach to minimize requests and allow for partial re-runs.

## Commands

### Setup
- Create virtual environment: `python3 -m venv venv`
- Activate virtual environment (macOS/Linux): `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### Running the Scraper
- Run all stages: `python src/cli.py` (Note: Only categories stage is fully implemented in CLI)
- Run specific stage: `python src/cli.py --stage categories`
- With custom delay: `python src/cli.py --delay 3.5`
- Resume from checkpoint: `python src/cli.py --resume`
- Dry run: `python src/cli.py --dry-run`

**Note**: While all three scrapers (categories, teams, contact) are implemented, the CLI currently only imports and runs the categories scraper. The teams and contact stages show "not yet implemented" messages.

### Stages
1. **Categories**: ✅ Scrape league/cup URLs from categories page with filters (implemented, handles cookie consent)
2. **Teams**: ✅ Extract team URLs from each league's tables page (implemented)
3. **Contact**: ✅ Scrape administrator contact info from team pages (implemented)

## Architecture

### Scraping Flow
1. **Categories Stage**:
   - Navigate to https://tulospalvelu.palloliitto.fi/categories
   - Apply filters: Football > South > Leagues and Cups > Boys > All ages
   - Save league/cup URLs to `data/intermediate/leagues.json`

2. **Teams Stage**:
   - Read league URLs from `leagues.json`
   - For each league, navigate to tables page
   - Extract all team URLs
   - Save to `data/intermediate/teams.json`

3. **Contact Stage**:
   - Read team URLs from `teams.json`
   - For each team, navigate to players page
   - Extract "Joukkueenjohtaja" from "Team officials" table
   - Save unique administrators with teams to `data/contacts.csv`

### Project Structure
- `src/`
  - `cli.py` - Command-line interface for staged execution
  - `main.py` - Legacy entry point (kept for backwards compatibility)
  - `pages/` - Page object models
    - `categories_page.py` - Categories page interactions
    - `teams_page.py` - League/cup tables page interactions
    - `contact_page.py` - Team players page interactions
  - `scrapers/` - Scraping logic for each stage
    - `categories_scraper.py` - Stage 1 implementation
    - `teams_scraper.py` - Stage 2 implementation
    - `contact_scraper.py` - Stage 3 implementation
  - `utils/`
    - `browser.py` - Selenium browser setup and management
- `config/`
  - `scraper.json` - Configuration for filters, delays, and output paths
- `data/` - Output directory (gitignored)
  - `intermediate/` - JSON files between stages
  - `contacts.csv` - Final output

## Important Notes

- Staged approach reduces server load and allows partial re-runs
- Intermediate data stored as JSON for easy parsing
- Configuration file controls filters, delays, and paths
- Browser runs non-headless by default (see config/scraper.json)
- Default delay between requests is 2 seconds
- The data_processor.py and checkpoint.py files mentioned do not exist in the utils folder
- Teams and contact stages in CLI are marked as TODO but the actual scrapers are implemented