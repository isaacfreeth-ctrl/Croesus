# European Political Donations Tracker

Search for company or individual donations to political parties across European jurisdictions.

## Jurisdictions Covered

| Country | Source | Threshold | Data Format |
|---------|--------|-----------|-------------|
| 🇬🇧 UK | Electoral Commission | £11,180 | API (CSV) |
| 🇩🇪 Germany | Bundestag | €35,000 | Web scraping |
| 🇦🇹 Austria | Rechnungshof | €500 | CSV |
| 🇪🇺 EU | APPF | €12,000 | Excel |

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
- Coverage: 2019-present
- CSV data from official publications
- Threshold: €500 for disclosure, €2,500 for immediate reporting
- Corporate donations allowed with no cap

### EU Authority for Political Parties (APPF)
- URL: https://www.appf.europa.eu
- Coverage: 2018-present
- Excel files from official website
- Covers European political parties (EPP, PES, ALDE, ECR, etc.)

## Notes

- Different countries have different disclosure thresholds
- Germany and Austria allow corporate donations
- France banned corporate donations in 1995
- UK requires donors to be UK-registered
- EU-level parties are distinct from national parties

## Example Searches

- Company names: "Microsoft", "Viessmann", "JCB"
- Individual names: Check donor lists in each jurisdiction
- Partial matches: "GmbH" (German companies), "Stiftung" (Austrian foundations)
