# European Political Donations Tracker

Search for company or individual donations to political parties across European jurisdictions.

## Jurisdictions Covered

| Country | Source | Threshold | Data Format | Years |
|---------|--------|-----------|-------------|-------|
| 🇬🇧 UK | Electoral Commission | £11,180 | API (CSV) | 2001+ |
| 🇩🇪 Germany | Bundestag | €35,000 | Web scraping | 2002+ |
| 🇦🇹 Austria | Rechnungshof | €500 | CSV | 2023-2025 |
| 🇮🇹 Italy | Parliament/TI Italia | €500 | CSV (GitHub) | 2018-2024 |
| 🇪🇺 EU | APPF | €12,000 | Excel | 2018+ |

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. Enter a company or individual name in the search box
2. Click "Search" to query all databases
3. View results by jurisdiction
4. Download Excel report with all data

## Data Sources

### UK Electoral Commission
- URL: https://search.electoralcommission.org.uk
- Coverage: 2001-present
- Direct API access with CSV export

### German Bundestag
- URL: https://www.bundestag.de/parlament/parteienfinanzierung
- Coverage: 2002-present (immediate disclosure)
- Web scraping of official publications
- Threshold changed from €50K to €35K in March 2024

### Austrian Rechnungshof (Court of Audit)
- URL: https://www.rechnungshof.gv.at
- Coverage: 2023-2025
- CSV data from official publications
- Threshold: €500 for disclosure, €2,500 for immediate reporting

### Italian Parliament / Transparency International Italia
- URL: https://soldiepolitica.it
- Data: https://github.com/ondata/liberiamoli-tutti
- Coverage: 2018-2024
- Threshold: €500 for disclosure, €5,000 for donor name
- Corporate donations allowed (€100K annual cap)
- Data aggregated by OnData from Parliament publications

### EU Authority for Political Parties (APPF)
- URL: https://www.appf.europa.eu
- Coverage: 2018-present
- Excel files from official website

## Example Searches

- Corporate: "SRL" (Italian companies), "GmbH" (German/Austrian companies), "Ltd" (UK)
- Specific: "Fininvest", "Ristonova", "JCB"
- Foundations: "Stiftung" (German), "Fondazione" (Italian)

## Data Highlights

### Italy (2024)
- €41M total donations
- 22,000+ donations
- ~930 corporate donations (€5.5M)
- Major parties: Forza Italia, Lega, FdI, M5S, PD

### Austria (2023-2025)
- 550 donations tracked
- Parties: SPÖ, ÖVP, NEOS, FPÖ, Die Grünen

## Notes

- Different countries have different disclosure thresholds
- Italy and Austria allow corporate donations
- Germany allows corporate donations with no cap
- France banned corporate donations in 1995
- UK requires donors to be UK-registered
- ~68% of Italian party donations come from MPs themselves
