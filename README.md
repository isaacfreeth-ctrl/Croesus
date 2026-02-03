# European Political Donations Tracker

Search for company/donor donations to political parties across multiple European jurisdictions.

## Features

- **Multi-jurisdiction search**: Enter a company name and search across UK, Germany (planned), and EU-level databases
- **UK Electoral Commission**: Full integration with live API - searches donations from 2001-present
- **Excel export**: Download comprehensive reports with:
  - Summary sheet with totals by jurisdiction
  - Raw data tabs for each country
  - Data sources documentation

## Data Sources

### Currently Implemented

| Country | Source | Coverage | Threshold |
|---------|--------|----------|-----------|
| 🇬🇧 UK | Electoral Commission | 2001-present | £11,180 (central), £2,230 (local) |

### Planned

| Country | Source | Coverage | Threshold |
|---------|--------|----------|-----------|
| 🇩🇪 Germany | Bundestag | 2002-present | €35,000 (immediate) |
| 🇪🇺 EU | APPF | 2018-present | €12,000 |
| 🇫🇷 France | HATVP | Varies | Bans corporate donations |
| 🇮🇪 Ireland | SIPO | Varies | €600 disclosure |

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

- `JCB` - Major Conservative donor
- `Unite` - Trade union donations
- `Dyson` - Manufacturing company
- Company names, individual names, or organisation names

## Output

The Excel report includes:

1. **Summary** - Overview with totals by jurisdiction
2. **UK - Electoral Commission** - Full raw data with all available fields
3. **Data Sources** - Documentation of sources, thresholds, and methodology

## Notes

- Different countries have different disclosure thresholds
- UK data is the most comprehensive and accessible
- Germany publishes large donations but not via a clean API
- Results may not capture all donations below disclosure thresholds

## Development

To add additional country sources:

1. Create a `search_[country]_donations()` function
2. Add the country to `DATA_SOURCES` dictionary
3. Add a worksheet in `create_excel_report()`
4. Update the search results display section

## License

For research and journalistic purposes.
