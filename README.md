# European Political Donations Tracker

Search for company/donor donations to political parties across multiple European jurisdictions.

## Features

- **Multi-jurisdiction search**: Enter a company name and search across UK and Germany databases
- **UK Electoral Commission**: Full integration with live API - searches donations from 2001-present
- **German Bundestag**: Live scraping of large donation disclosures (>€35K)
- **Excel export**: Download comprehensive reports with:
  - Summary sheet with totals by jurisdiction
  - Raw data tabs for each country
  - Data sources documentation

## Data Sources

### Currently Implemented

| Country | Source | Coverage | Threshold |
|---------|--------|----------|-----------|
| 🇬🇧 UK | Electoral Commission | 2001-present | £11,180 (central), £2,230 (local) |
| 🇩🇪 Germany | Bundestag | 2020-present | €35,000 (since Mar 2024), €50,000 (before) |

### Planned

| Country | Source | Coverage | Threshold |
|---------|--------|----------|-----------|
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

**UK donors:**
- `JCB` - Major Conservative donor
- `Unite` - Trade union donations
- `Dyson` - Manufacturing company

**German donors:**
- `Viessmann` - Multi-party donor
- `Maschmeyer` - Individual donor to CDU/FDP
- `Quandt` - BMW family donations

## Output

The Excel report includes:

1. **Summary** - Overview with totals by jurisdiction (£ for UK, € for Germany)
2. **UK - Electoral Commission** - Full raw data with all available fields
3. **Germany - Bundestag** - Scraped donation data with party, amount, donor details
4. **Data Sources** - Documentation of sources, thresholds, and methodology

## Notes

- Different countries have different disclosure thresholds
- UK data is the most comprehensive with lower thresholds
- German data only includes large donations (>€35K since March 2024)
- Results may not capture all donations below disclosure thresholds

## Technical Details

### Germany Scraping

The German Bundestag publishes large party donations as HTML tables on their website. This tool scrapes:
- 2025: https://www.bundestag.de/parlament/praesidium/parteienfinanzierung/fundstellen50000/2025/
- 2024: https://www.bundestag.de/parlament/praesidium/parteienfinanzierung/fundstellen50000/2024/

Data includes: Party, Amount, Donor name and address, Date received

### UK API

Uses the Electoral Commission's CSV export API:
- Base URL: `https://search.electoralcommission.org.uk/api/csv/Donations`
- Returns: Full donation records including donor details, party, amounts, dates

## Development

To add additional country sources:

1. Create a `search_[country]_donations()` function
2. Add the country to `DATA_SOURCES` dictionary
3. Add a worksheet in `create_excel_report()`
4. Update the search results display section

## License

For research and journalistic purposes.
