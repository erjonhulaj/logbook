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
    context: str = ""


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

    if entry.get("why"):
        print(f"Why: {entry['why']}")
    if entry.get("alternatives"):
        print(f"Alternatives: {entry['alternatives']}")
    if entry.get("context"):
        print(f"Context: {entry['context']}")
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
    entry_type = click.prompt("Type (decision/win)")
    what = click.prompt("What happened?")
    
    if entry_type == "decision":
        why = click.prompt("Why did you make this decision?")
        alternatives = click.prompt("What alternatives did you consider?")
    elif entry_type == "win":
        context = click.prompt("What's the context? (project, topic, etc.)")
    else:
        print("Unknown entry type. Please choose 'decision' or 'win'.")
        return
   
    tags = click.prompt("Tags (comma separated)").split(",")
    # Remove extra spaces and empty tags
    tags = [tag.strip() for tag in tags if tag.strip()]
    entry = Entry(
        type=entry_type,
        what=what,
        why=why if entry_type == "decision" else "",
        alternatives=alternatives if entry_type == "decision" else "",
        tags=tags,
        context=context if entry_type == "win" else ""
    )
    save_entry(entry)
    print("Entry saved!")

# Command to view all entries in the logbook.
@cli.command()
@click.option("--type", "entry_type", default=None, help="Filter by entry type (e.g. decision, win)")
@click.option("--limit", default=10, help="Limit the number of entries displayed")
@click.option("--tags", default=None, help="Filter by tags (comma separated)")

def view(entry_type, limit, tags):
    entries = load_entries()
    
    if entry_type:
        entries = [e for e in entries if e["type"] == entry_type]
    
    if tags:
        filter_tags = set(tag.strip() for tag in tags.split(","))
        entries = [e for e in entries if filter_tags.intersection(set(e["tags"]))]
    
    if not entries:
        print("No entries found.")
        return
    
    for entry in entries[:limit]:
        print_entry(entry)

@cli.command()
@click.argument("query")
def search(query):
    entries = load_entries()
    query = query.lower()
    results = []
    
    for entry in entries:
        if (query in entry["what"].lower() or
            query in entry.get("why", "").lower() or
            query in entry.get("alternatives", "").lower() or
            query in entry.get("context", "").lower() or
            query in " ".join(entry["tags"]).lower()):
            results.append(entry)
    
    if not results:
        print("No matching entries found.")
        return
    
    for entry in results:
        print_entry(entry)

@cli.command()
@click.option("--output", default="logbook.md", help="Output file for markdown export")
def export(output):
    entries = load_entries()
    with open(output, "w") as f:
        for entry in entries:
            f.write(f"## [{entry['type']}] {entry['timestamp']}\n\n")
            f.write(f"**What:** {entry['what']}\n\n")
            if entry.get("why"):
                f.write(f"**Why:** {entry['why']}\n\n")
            if entry.get("alternatives"):
                f.write(f"**Alternatives:** {entry['alternatives']}\n\n")
            if entry.get("context"):
                f.write(f"**Context:** {entry['context']}\n\n")
            if entry.get("tags"):
                f.write(f"**Tags:** {', '.join(entry['tags'])}\n\n")
            f.write("---\n\n")
    print(f"Exported {len(entries)} entries to {output}")
        

if __name__ == "__main__":
    cli()

