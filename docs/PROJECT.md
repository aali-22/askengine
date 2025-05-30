# AskEngine Sports Data Project Documentation

## Project Overview
AskEngine is a comprehensive sports data pipeline that collects, organizes, and analyzes MLB and NBA data from 2010 onwards. The project aims to provide complete historical data for both sports, including regular season stats, playoff performances, and notable records.

## Data Requirements

### MLB Data Requirements (2010-2025)
For each season, we need:

1. **Team Data** (`data/baseball/{year}/{team_abbr}.json`)
   - Regular season record (W-L)
   - Team statistics
   - Roster information
   - Player statistics

2. **League Data** (`data/baseball/{year}/league/`)
   - `standings.json`: Final regular season standings
   - `records.json`: Notable season records
     - Most home runs
     - Most hits in a game
     - Perfect games
     - No-hitters
     - Immaculate innings
     - Other notable achievements

3. **Player Data** (`data/baseball/{year}/players/`)
   - Regular season averages
   - Playoff statistics
   - Career milestones
   - Awards and achievements

### NBA Data Requirements (2010-2025)
For each season, we need:

1. **Team Data** (`data/basketball/{year}/{team_abbr}.json`)
   - Regular season record (W-L)
   - Team statistics
   - Roster information
   - Player statistics

2. **League Data** (`data/basketball/{year}/league/`)
   - `standings.json`: Final regular season standings
   - `records.json`: Notable season records
     - Most points in a game
     - Most assists in a game
     - Most rebounds in a game
     - Triple doubles
     - Other notable achievements

3. **Player Data** (`data/basketball/{year}/players/`)
   - Regular season averages
   - Playoff statistics
   - Career milestones
   - Awards and achievements

## Project Structure

```
askengine/
├── scripts/
│   ├── fetchers/           # Data fetching scripts
│   │   ├── mlb_fetcher.py  # MLB data fetcher
│   │   └── nba_fetcher.py  # NBA data fetcher
│   ├── organizers/         # Data organization scripts
│   │   ├── mlb_organizer.py
│   │   └── nba_organizer.py
│   ├── uploaders/          # AWS upload scripts
│   │   ├── s3_uploader.py
│   │   └── config.py
│   └── utils/             # Utility scripts
│       ├── cleanup.py
│       └── restore_mlb.py
├── data/
│   ├── baseball/          # MLB data by season
│   │   ├── 2025/
│   │   ├── 2024/
│   │   └── ...
│   └── basketball/        # NBA data by season
│       ├── 2025/
│       ├── 2024/
│       └── ...
└── docs/                  # Documentation
    └── PROJECT.md
```

## Data Collection Workflow

1. **Initial Data Collection (2010-2025)**
   - Fetch current season data
   - Fetch historical data from 2010
   - Organize into proper structure
   - Validate data completeness

2. **Historical Data Collection (2000-2009)**
   - Fetch data for each season
   - Organize into proper structure
   - Validate data completeness

3. **Pre-2000 Data Collection**
   - Evaluate data availability
   - Plan collection strategy
   - Implement data collection

## Current Status

### MLB Data Status
- [ ] 2025 Season
- [ ] 2024 Season
- [ ] 2023 Season
- [ ] 2022 Season
- [ ] 2021 Season
- [ ] 2020 Season
- [ ] 2019 Season
- [ ] 2018 Season
- [ ] 2017 Season
- [ ] 2016 Season
- [ ] 2015 Season
- [ ] 2014 Season
- [ ] 2013 Season
- [ ] 2012 Season
- [ ] 2011 Season
- [ ] 2010 Season

### NBA Data Status
- [ ] 2025 Season
- [ ] 2024 Season
- [ ] 2023 Season
- [ ] 2022 Season
- [ ] 2021 Season
- [ ] 2020 Season
- [ ] 2019 Season
- [ ] 2018 Season
- [ ] 2017 Season
- [ ] 2016 Season
- [ ] 2015 Season
- [ ] 2014 Season
- [ ] 2013 Season
- [ ] 2012 Season
- [ ] 2011 Season
- [ ] 2010 Season

## Script Descriptions

### Fetchers
- `mlb_fetcher.py`: Fetches MLB data from official API
- `nba_fetcher.py`: Fetches NBA data from official API

### Organizers
- `mlb_organizer.py`: Organizes MLB data into proper structure
- `nba_organizer.py`: Organizes NBA data into proper structure

### Uploaders
- `s3_uploader.py`: Uploads data to AWS S3
- `config.py`: AWS configuration settings

### Utils
- `cleanup.py`: Cleans up data files
- `restore_mlb.py`: Restores MLB team files if needed

## Data Validation

Each data file should be validated for:
1. Completeness (all required fields present)
2. Accuracy (data matches official sources)
3. Consistency (format matches other seasons)
4. Integrity (no corrupted data)

## Next Steps

1. **Immediate Tasks**
   - Complete 2023-2025 data collection
   - Implement data validation
   - Set up automated testing

2. **Short-term Goals**
   - Complete 2010-2022 data collection
   - Implement data quality checks
   - Set up automated uploads

3. **Long-term Goals**
   - Collect 2000-2009 data
   - Evaluate pre-2000 data availability
   - Implement data analysis tools

## Data Sources

### MLB
- Official MLB API
- Baseball-Reference
- FanGraphs

### NBA
- Official NBA API
- Basketball-Reference
- NBA Stats

## Contributing

Please read [CONTRIBUTING.md](../CONTRIBUTING.md) for details on how to contribute to this project. 