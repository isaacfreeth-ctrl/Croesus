# European Political Donations Tracker

Search for company or individual donations to political parties across European jurisdictions.

## Jurisdictions Covered

| Country | Source | Threshold | Data Format | Years |
|---------|--------|-----------|-------------|-------|
| 🇬🇧 UK | Electoral Commission | £11,180 | API (CSV) | 2001+ |
| 🇩🇪 Germany | Bundestag | €35,000 | Web scraping | 2002+ |
| 🇦🇹 Austria | Rechnungshof | €500 | CSV | 2023-2025 |
| 🇮🇹 Italy | Parliament/TI Italia | €500 | CSV (GitHub) | 2018-2024 |
| 🇳🇱 Netherlands | Ministry BZK | €10,000 | ODS | 2023-2024 |
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
- Threshold: €500 for disclosure
- Corporate donations allowed (€100K annual cap)

### Dutch Ministry of Interior (BZK)
- URL: https://www.rijksoverheid.nl
- Coverage: 2023-2024
- ODS (OpenDocument Spreadsheet) files
- Threshold: €10,000 for immediate disclosure, €1,000 for annual reports
- Foreign donations banned, max €100K per donor
- Most donations from politicians (GL, SP especially)

### EU Authority for Political Parties (APPF)
- URL: https://www.appf.europa.eu
- Coverage: 2018-present
- Excel files from official website

## Example Searches

- Corporate (NL): "B.V.", "Stichting", "Fonds", "Holding"
- Corporate (IT): "SRL", "SPA", "Società"
- Corporate (DE/AT): "GmbH", "AG", "Stiftung"
- Corporate (UK): "Ltd", "PLC"

## Data Highlights

### Netherlands (2023-2024)
- ~500 donations tracked (>€10K threshold)
- Total: ~€9M
- Most donations are from politicians to their own parties
- Corporate donors: ~65 (B.V., Stichting, Fonds)
- Major parties: SP, GL, VVD, D66, FvD, Volt

### Regulatory Notes
- Netherlands: Foreign donations BANNED since 2023
- Netherlands: Max €100K per donor per year
- Netherlands: €10K+ must be reported within 3 days
- Italy: Foreign donations restricted
- Germany: No cap on individual donations
- UK: Donors must be UK-registered

## Notes

- Different countries have different disclosure thresholds
- Netherlands has highest disclosure threshold (€10K)
- Austria has lowest threshold (€500)
- Most Dutch party funding comes from MP contributions
- Corporate influence more visible in Italy, Germany
