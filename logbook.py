import json
import os
import click
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from dataclasses import asdict

# Single entry in the logbook. It has all the fields that we want to store for each entry.
@dataclass
class Entry:
    type: str
    what: str
    why: str
    alternatives: str
    tags: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# Save an entry to the logbook.

# Path to the logbook data file.
DATA_FILE = os.path.expanduser("~/.logbook/logbook.json")

def save_entry(entry: Entry):
    # Create the storage directory if it doesn't exist yet
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    entries = load_entries()
    entries.append(asdict(entry))

    with open(DATA_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def load_entries ():
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, "r") as f:
        return json.load(f)
    
# Print an entry in a readable format.
def print_entry(entry: dict):
    print(f"Type: {entry['type']}")
    print(f"What: {entry['what']}")
    print(f"Why: {entry['why']}")
    print(f"Alternatives: {entry['alternatives']}")
    print(f"Tags: {', '.join(entry['tags'])}")
    print(f"Timestamp: {entry['timestamp']}")
    print("-" * 40)

# Command-line interface using Click
@click.group()
def cli():
    pass

# Command to add and save a new entry to the logbook.
@cli.command()
def add():
    entry_type = click.prompt("Type (e.g. decision, action, event)")
    what = click.prompt("What happened?")
    why = click.prompt("Why did it happen?")
    alternatives = click.prompt("What were the alternatives?")
    tags = click.prompt("Tags (comma separated)").split(",")

    entry = Entry(type=entry_type, what=what, why=why, alternatives=alternatives, tags=[tag.strip() for tag in tags])
    save_entry(entry)
    print("Entry saved!")

# Command to view all entries in the logbook.
@cli.command()
def view():
    entries = load_entries()
    if not entries:
        print("No entries found.")
        return
    
    for entry in entries:
        print_entry(entry)

if __name__ == "__main__":
    cli()

