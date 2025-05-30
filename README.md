# AskEngine Sports Data Pipeline

A comprehensive sports data pipeline for fetching, organizing, and analyzing MLB and NBA data.

## Project Structure

```
askengine/
├── scripts/
│   ├── fetchers/      # Data fetching scripts
│   ├── organizers/    # Data organization scripts
│   ├── uploaders/     # AWS upload scripts
│   └── utils/         # Utility scripts
├── data/
│   ├── baseball/      # MLB data by season
│   └── basketball/    # NBA data by season
└── tests/            # Test files
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-2
S3_BUCKET_NAME=askengine-data

# Upload Settings
UPLOAD_BATCH_SIZE=100
RETRY_ATTEMPTS=3
RETRY_DELAY=5

# Logging
LOG_LEVEL=INFO
```

## Usage

### Fetching Data

```bash
# Fetch MLB data for seasons 2010-2022
python scripts/fetchers/mlb_fetcher.py

# Fetch NBA data
python scripts/fetchers/nba_fetcher.py
```

### Organizing Data

```bash
# Organize MLB data
python scripts/organizers/mlb_organizer.py

# Organize NBA data
python scripts/organizers/nba_organizer.py
```

### Uploading to AWS

```bash
# Upload data to S3
python scripts/uploaders/s3_uploader.py
```

## Data Structure

Check wiki

### Running Tests
```bash
python -m pytest tests/
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 