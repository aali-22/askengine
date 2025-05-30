# AskEngine - Unified Sports Query Engine

AskEngine is a natural language query system for sports statistics, powering AskLabs' suite of sport-specific intelligence tools. It enables users to query sports data using natural language and get structured, accurate responses.

## Features

- Natural language processing for sports queries
- Support for multiple sports domains:
  - ⚽ AskFooty (Soccer/Football)
  - ⚾ AskSlugger (Baseball)
  - 🏀 AskHoop (Basketball)
- Structured data responses
- CLI interface

## Installation

```bash
# Clone the repository
git clone https://github.com/aali-22/askengine.git
cd askengine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
askengine/
├── askfooty/              # Soccer-specific module
├── askhoop/               # Basketball module
├── askslugger/            # Baseball module
├── askengine_core/        # Shared core logic
├── cli/                   # CLI interface
├── web/                   # Web server (optional)
├── docs/                  # Documentation
└── tests/                 # Test suite
```

## Usage

```bash
# Run via CLI
python cli/run_cli.py "Who had the most goals in La Liga 2014?"

# Run tests
pytest tests/
```

## Data Sources

This project uses publicly available sports statistics from:
- FBref (Soccer)
- Baseball-Reference
- Basketball-Reference

All data usage complies with fair use policies and provides proper attribution.

## Acknowledgments

- Data providers: FBref, Baseball-Reference, Basketball-Reference
- Open source community for various tools and libraries used in this project 
