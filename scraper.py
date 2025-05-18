#!/usr/bin/env python3
"""
Interactive CLI for the Finnish Soccer League scraper.
"""

import logging
from datetime import datetime
from pathlib import Path
import json

from src.scrapers.categories_scraper import CategoriesScraper

# Set up logging to both console and file
def setup_logging():
    """Set up logging to both console and file."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"scraper_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Console output
        ]
    )
    
    # Set specific loggers to appropriate levels
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return log_file

# Set up logging
log_file = setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {log_file}")


def print_menu():
    """Print the main menu."""
    print("\n=== Finnish Soccer League Scraper ===")
    print("\nStages:")
    print("1. Categories - Get league/cup URLs")
    print("2. Teams - Get team URLs from leagues")
    print("3. Contact - Get administrator contact info")
    print("\nActions:")
    print("4. Run all stages")
    print("5. Explore categories page (visual mode)")
    print("6. View saved data")
    print("7. Settings")
    print("8. View logs")
    print("0. Exit")
    print("")


def run_categories(config):
    """Run the categories stage."""
    print("\nRunning Categories stage...")
    logger.info("Starting Categories stage")
    try:
        scraper = CategoriesScraper()
        scraper.scrape(
            delay=config.get("delay", 2.0),
            resume=config.get("resume", False),
            dry_run=config.get("dry_run", False)
        )
        print("Categories stage completed!")
        logger.info("Categories stage completed successfully")
    except Exception as e:
        logger.error(f"Categories stage failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        print(f"Check the log file for details: {log_file}")


def run_teams(config):
    """Run the teams stage."""
    print("\nRunning Teams stage...")
    print("Teams stage not yet implemented.")


def run_contact(config):
    """Run the contact stage."""
    print("\nRunning Contact stage...")
    print("Contact stage not yet implemented.")


def run_all_stages(config):
    """Run all stages in sequence."""
    print("\nRunning all stages...")
    run_categories(config)
    run_teams(config)
    run_contact(config)
    print("\nAll stages completed!")


def explore_categories():
    """Explore categories page in visual mode."""
    print("\nOpening browser for exploration...")
    logger.info("Starting categories exploration")
    try:
        scraper = CategoriesScraper()
        scraper.explore()
    except Exception as e:
        logger.error(f"Exploration failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        print(f"Check the log file for details: {log_file}")


def view_saved_data():
    """View saved data from different stages."""
    print("\n=== Saved Data ===")
    
    # Check for leagues data
    leagues_file = Path("data/intermediate/leagues.json")
    if leagues_file.exists():
        with open(leagues_file) as f:
            data = json.load(f)
        print(f"\nCategories: {len(data.get('leagues', []))} leagues/cups found")
        print(f"Last run: {data.get('timestamp', 'Unknown')}")
        print("\nFirst 5 leagues:")
        for i, league in enumerate(data.get('leagues', [])[:5], 1):
            print(f"{i}. {league.get('name', 'Unknown')}")
    else:
        print("\nNo categories data found. Run stage 1 first.")
    
    # Check for teams data (will be added later)
    teams_file = Path("data/intermediate/teams.json")
    if teams_file.exists():
        with open(teams_file) as f:
            data = json.load(f)
        print(f"\nTeams: {len(data.get('teams', []))} teams found")
    
    # Check for contacts data
    contacts_file = Path("data/contacts.csv")
    if contacts_file.exists():
        print(f"\nContacts: File exists at {contacts_file}")


def view_logs():
    """View recent log entries."""
    print("\n=== Recent Log Entries ===")
    print(f"Current log file: {log_file}")
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Show last 20 lines
            recent_lines = lines[-20:] if len(lines) > 20 else lines
            print("\nLast 20 log entries:")
            for line in recent_lines:
                print(line.strip())
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    print("\nAll logs are saved in the 'logs' directory.")


def edit_settings(config):
    """Edit scraper settings."""
    print("\n=== Settings ===")
    print(f"1. Request delay: {config['delay']} seconds")
    print(f"2. Resume from checkpoint: {config['resume']}")
    print(f"3. Dry run mode: {config['dry_run']}")
    print(f"4. Headless browser: {config['headless']}")
    print("0. Back to main menu")
    
    choice = input("\nSelect setting to change: ")
    
    if choice == "1":
        try:
            new_delay = float(input("Enter new delay (seconds): "))
            config["delay"] = new_delay
            print(f"Delay set to {new_delay} seconds")
        except ValueError:
            print("Invalid number")
    elif choice == "2":
        config["resume"] = not config["resume"]
        print(f"Resume mode: {config['resume']}")
    elif choice == "3":
        config["dry_run"] = not config["dry_run"]
        print(f"Dry run mode: {config['dry_run']}")
    elif choice == "4":
        config["headless"] = not config["headless"]
        print(f"Headless browser: {config['headless']}")
        # Update the config file
        with open("config/scraper.json", "r+") as f:
            file_config = json.load(f)
            file_config["browser"]["headless"] = config["headless"]
            f.seek(0)
            json.dump(file_config, f, indent=2)
            f.truncate()
    
    return config


def main():
    """Main interactive CLI loop."""
    # Create necessary directories
    for dir_path in ['data', 'data/intermediate', 'logs']:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Load default config
    config = {
        "delay": 2.0,
        "resume": False,
        "dry_run": False,
        "headless": True
    }
    
    # Load config file
    config_file = Path("config/scraper.json")
    if config_file.exists():
        with open(config_file) as f:
            file_config = json.load(f)
            config["headless"] = file_config.get("browser", {}).get("headless", True)
    
    print("Welcome to the Finnish Soccer League Scraper!")
    print("This tool extracts team administrator contact information.")
    
    while True:
        print_menu()
        choice = input("Select an option: ")
        
        try:
            if choice == "0":
                print("\nExiting...")
                break
            elif choice == "1":
                run_categories(config)
            elif choice == "2":
                run_teams(config)
            elif choice == "3":
                run_contact(config)
            elif choice == "4":
                run_all_stages(config)
            elif choice == "5":
                explore_categories()
            elif choice == "6":
                view_saved_data()
            elif choice == "7":
                config = edit_settings(config)
            elif choice == "8":
                view_logs()
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\nAn error occurred: {e}")
            print(f"Check the log file for details: {log_file}")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
