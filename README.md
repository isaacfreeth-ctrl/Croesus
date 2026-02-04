# European Political Donations Tracker

Search for company/donor donations to political parties across multiple European jurisdictions.

## Features

- **Multi-jurisdiction search**: Enter a company name and search across UK, Germany, and EU-level databases
- **UK Electoral Commission**: Full integration with live API - searches donations from 2001-present
- **German Bundestag**: Live scraping of large donation disclosures (>€35K)
- **EU APPF**: Downloads and parses official European Political Party donation files
- **Excel export**: Download comprehensive reports with:
  - Summary sheet with totals by jurisdiction
  - Raw data tabs for each country/level
  - Data sources documentation

## Data Sources

| Country | Source | Coverage | Threshold |
|---------|--------|----------|-----------|
| 🇬🇧 UK | Electoral Commission | 2001-present | £11,180 (central), £2,230 (local) |
| 🇩🇪 Germany | Bundestag | 2020-present | €35,000 (since Mar 2024), €50,000 (before) |
| 🇪🇺 EU | APPF | 2018-present | €12,000 |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

## Search Examples

**UK donors:**
- `JCB` - Major Conservative donor
- `Unite` - Trade union donations

**German donors:**
- `Viessmann` - Multi-party donor (CDU, CSU, SPD, FDP, Grüne)
- `Maschmeyer` - Individual donor

**EU-level donors:**
- `Microsoft` - Tech company donations to ALDE
- `AT&T` - Telecom donations to multiple European parties

## Output

The Excel report includes:

1. **Summary** - Overview with totals by jurisdiction (£ for UK, € for Germany/EU)
2. **UK - Electoral Commission** - Full raw data
3. **Germany - Bundestag** - Scraped donation data
4. **EU - APPF** - European political party donations
5. **Data Sources** - Methodology documentation

## Notes

- Different jurisdictions have different disclosure thresholds
- UK data is most comprehensive with lower thresholds
- German data only includes large donations (>€35K since March 2024)
- EU data covers European-level political parties (EPP, S&D, ALDE, etc.)
- Corporate donations are allowed in UK, Germany, and at EU level
- France bans corporate donations (not included in this tool)

## Technical Details

### Data Retrieval Methods

| Source | Method | Format |
|--------|--------|--------|
| UK | REST API (CSV export) | CSV |
| Germany | Web scraping | HTML tables |
| EU APPF | Direct download | Excel files |

## License

For research and journalistic purposes.
