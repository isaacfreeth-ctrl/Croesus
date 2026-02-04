"""
European Political Donations Tracker
Search for company donations across multiple European jurisdictions
"""

import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import time
import re
from typing import Optional
import xml.etree.ElementTree as ET

# Page config
st.set_page_config(
    page_title="European Political Donations Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 European Political Donations Tracker")
st.markdown("""
Search for company or individual donations to political parties across European jurisdictions.
Enter a company name to search across available databases.
""")

# Data source info
DATA_SOURCES = {
    "uk": {
        "name": "UK Electoral Commission",
        "coverage": "2001-present",
        "threshold": "£11,180 (central), £2,230 (accounting units)",
        "url": "https://search.electoralcommission.org.uk"
    },
    "germany": {
        "name": "German Bundestag",
        "coverage": "2002-present (immediate disclosure >€35K)",
        "threshold": "€35,000 (immediate), €10,000 (annual reports)",
        "url": "https://www.bundestag.de/parlament/parteienfinanzierung"
    },
    "eu": {
        "name": "EU Authority for Political Parties",
        "coverage": "2018-present",
        "threshold": "€12,000",
        "url": "https://www.appf.europa.eu"
    }
}

# Sidebar with data source info
with st.sidebar:
    st.header("📊 Data Sources")
    for key, source in DATA_SOURCES.items():
        with st.expander(f"🔹 {source['name']}"):
            st.write(f"**Coverage:** {source['coverage']}")
            st.write(f"**Threshold:** {source['threshold']}")
            st.link_button("Visit source", source['url'])
    
    st.divider()
    st.markdown("### ⚙️ Search Settings")
    search_years = st.slider(
        "Years to search",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of years back to search"
    )
    
    st.divider()
    st.markdown("""
    ### About
    This tool searches publicly available political donation 
    records across European jurisdictions.
    
    **Note:** Different countries have different disclosure 
    thresholds and reporting requirements. Results may not 
    be comprehensive.
    """)


# ============= UK ELECTORAL COMMISSION =============

def search_uk_donations(query: str, years: int = 5) -> pd.DataFrame:
    """
    Search UK Electoral Commission donations database.
    API endpoint allows CSV export with query parameters.
    """
    base_url = "https://search.electoralcommission.org.uk/api/csv/Donations"
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    params = {
        "start": 0,
        "rows": 500,
        "query": query,
        "sort": "AcceptedDate",
        "order": "desc",
        "et": "pp",  # Political parties
        "date": "Accepted",
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "prePoll": "false",
        "postPoll": "true"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code == 200 and response.content:
            df = pd.read_csv(BytesIO(response.content))
            if not df.empty:
                # Clean up column names
                df.columns = df.columns.str.strip()
                
                # Convert Value from string (£500,000.00) to numeric
                if 'Value' in df.columns:
                    df['ValueNumeric'] = df['Value'].str.replace('£', '').str.replace(',', '').astype(float)
                
                # Parse dates
                if 'AcceptedDate' in df.columns:
                    df['AcceptedDate'] = pd.to_datetime(df['AcceptedDate'], format='%d/%m/%Y', errors='coerce')
                
                # Add source column
                df['Source'] = 'UK Electoral Commission'
                return df
    except Exception as e:
        st.warning(f"UK search error: {str(e)}")
    
    return pd.DataFrame()


def format_uk_results(df: pd.DataFrame) -> pd.DataFrame:
    """Format UK results for display."""
    if df.empty:
        return df
    
    # Select and rename key columns
    column_map = {
        'DonorName': 'Donor',
        'AccountingUnitName': 'Recipient',
        'RegulatedEntityName': 'Party',
        'Value': 'Amount (£)',
        'AcceptedDate': 'Date',
        'DonorStatus': 'Donor Type',
        'DonationType': 'Donation Type',
        'NatureOfDonation': 'Nature',
        'IsSponsorship': 'Sponsorship'
    }
    
    available_cols = [c for c in column_map.keys() if c in df.columns]
    result = df[available_cols].copy()
    result = result.rename(columns={k: v for k, v in column_map.items() if k in available_cols})
    
    return result


# ============= GERMANY (Bundestag Scraper) =============

def scrape_bundestag_year(year: int) -> pd.DataFrame:
    """Scrape donations from Bundestag website for a given year."""
    from bs4 import BeautifulSoup
    
    # URL patterns - the suffix changes each year
    url_patterns = {
        2025: 'https://www.bundestag.de/parlament/praesidium/parteienfinanzierung/fundstellen50000/2025/2025-inhalt-1032412',
        2024: 'https://www.bundestag.de/parlament/praesidium/parteienfinanzierung/fundstellen50000/2024/2024-inhalt-984862',
        2023: 'https://www.bundestag.de/parlament/praesidium/parteienfinanzierung/fundstellen50000/2023',
        2022: 'https://www.bundestag.de/parlament/praesidium/parteienfinanzierung/fundstellen50000/2022/2022-inhalt-879480',
        2021: 'https://www.bundestag.de/parlament/praesidium/parteienfinanzierung/fundstellen50000/2021/2021-inhalt-816896',
        2020: 'https://www.bundestag.de/parlament/praesidium/parteienfinanzierung/fundstellen50000/2020/2020-inhalt-678704',
    }
    
    url = url_patterns.get(year)
    if not url:
        return pd.DataFrame()
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    
    if not tables:
        return pd.DataFrame()
    
    table = tables[0]
    rows = table.find_all('tr')
    
    donations = []
    current_month = None
    
    for row in rows[1:]:  # Skip header
        cells = row.find_all(['td', 'th'])
        
        # Month header row (single cell)
        if len(cells) == 1:
            current_month = cells[0].get_text(strip=True)
            continue
        
        # Data row
        if len(cells) >= 4:
            party = cells[0].get_text(strip=True)
            amount_text = cells[1].get_text(strip=True)
            donor_raw = cells[2].get_text(strip=True)
            date_received = cells[3].get_text(strip=True)
            
            # Parse amount
            amount_match = re.search(r'([\d.,]+)\s*Euro', amount_text)
            if amount_match:
                amount_str = amount_match.group(1).replace('.', '').replace(',', '.')
                try:
                    amount = float(amount_str)
                except:
                    amount = 0
            else:
                amount = 0
            
            # Clean donor name (remove address parts for display)
            donor_parts = re.split(r'(?<=[a-zäöü])(?=[A-ZÄÖÜ0-9])|(?<=\.)(?=[A-Z])', donor_raw)
            donor_name = donor_parts[0] if donor_parts else donor_raw
            
            donations.append({
                'Year': year,
                'Month': current_month,
                'Party': party,
                'Amount': amount,
                'AmountText': amount_text,
                'Donor': donor_name,
                'DonorFull': donor_raw,
                'DateReceived': date_received,
                'Source': 'German Bundestag'
            })
    
    return pd.DataFrame(donations)


def search_germany_donations(query: str, years: int = 5) -> pd.DataFrame:
    """
    Search German party donations by scraping Bundestag website.
    Returns donations matching the search query.
    """
    current_year = datetime.now().year
    all_donations = []
    
    # Scrape each year
    years_to_search = range(current_year, current_year - years - 1, -1)
    
    for year in years_to_search:
        df = scrape_bundestag_year(year)
        if not df.empty:
            all_donations.append(df)
    
    if not all_donations:
        return pd.DataFrame()
    
    combined = pd.concat(all_donations, ignore_index=True)
    
    # Filter by search query (case-insensitive search in donor field)
    query_lower = query.lower()
    mask = combined['DonorFull'].str.lower().str.contains(query_lower, na=False)
    
    results = combined[mask].copy()
    
    return results


def format_germany_results(df: pd.DataFrame) -> pd.DataFrame:
    """Format German results for display."""
    if df.empty:
        return df
    
    display_cols = ['Donor', 'Party', 'Amount', 'DateReceived', 'Year']
    available = [c for c in display_cols if c in df.columns]
    result = df[available].copy()
    
    # Rename for display
    result = result.rename(columns={
        'Amount': 'Amount (€)',
        'DateReceived': 'Date Received'
    })
    
    return result


# ============= EU LEVEL (APPF) =============

def download_eu_donations_file(url: str) -> bytes:
    """Download EU donations Excel file."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        st.warning(f"Failed to download EU data: {e}")
    return None


def parse_eu_donations_excel(content: bytes, year: int) -> list:
    """Parse EU APPF donations Excel file."""
    if not content:
        return []
    
    try:
        df = pd.read_excel(BytesIO(content), header=None)
    except:
        return []
    
    donations = []
    current_party = None
    
    for i, row in df.iterrows():
        val0 = str(row[0]) if pd.notna(row[0]) else ''
        val1 = str(row[1]) if pd.notna(row[1]) else ''
        val2 = str(row[2]) if pd.notna(row[2]) else ''
        
        # Party header (starts with Ø or is a standalone party name)
        if val0.startswith('Ø') or (val0 and not val1 and not val2 and len(val0) > 10 and 
            any(x in val0 for x in ['Party', 'Movement', 'Alliance', 'Democrats', 'Conservatives'])):
            current_party = val0.replace('Ø', '').replace('\xa0', ' ').strip()
            continue
        
        # Skip header rows
        if val0.strip().lower() in ['donor', 'donor ']:
            continue
        
        # Data row - has country and numeric value
        if current_party and val1 and val2:
            try:
                amount = float(str(val2).replace(',', '').replace(' ', ''))
                donations.append({
                    'Party': current_party,
                    'Donor': val0.strip(),
                    'Country': val1.strip(),
                    'Amount': amount,
                    'Year': year,
                    'Source': 'EU APPF'
                })
            except:
                pass
    
    return donations


def search_eu_donations(query: str) -> pd.DataFrame:
    """
    Search EU Authority for Political Parties and Foundations.
    Downloads and parses Excel files from APPF website.
    """
    # EU APPF Excel file URLs
    eu_files = {
        2025: "https://www.appf.europa.eu/cmsdata/299571/2025%20PARTIES%20Donations%20table%20as%20of%202025-11-03.xlsx",
        2024: "https://www.appf.europa.eu/cmsdata/291887/2024%20PARTIES%20Donations%20table%20as%20of%202024-12-04.xlsx",
    }
    
    all_donations = []
    
    for year, url in eu_files.items():
        content = download_eu_donations_file(url)
        if content:
            donations = parse_eu_donations_excel(content, year)
            all_donations.extend(donations)
    
    if not all_donations:
        st.warning("No EU donation data could be loaded. Check network connection.")
        return pd.DataFrame()
    
    # Convert to DataFrame and search
    df = pd.DataFrame(all_donations)
    
    # Filter by query (case-insensitive search in Donor field)
    query_lower = query.lower()
    mask = df['Donor'].str.lower().str.contains(query_lower, na=False)
    
    return df[mask].copy()


def format_eu_results(df: pd.DataFrame) -> pd.DataFrame:
    """Format EU results for display."""
    if df.empty:
        return df
    
    display_cols = ['Donor', 'Party', 'Amount', 'Country', 'Year']
    available = [c for c in display_cols if c in df.columns]
    result = df[available].copy()
    
    result = result.rename(columns={
        'Amount': 'Amount (€)'
    })
    
    return result


# ============= EXCEL EXPORT =============

def create_excel_report(company_name: str, uk_data: pd.DataFrame, germany_data: pd.DataFrame = None, eu_data: pd.DataFrame = None) -> BytesIO:
    """
    Create multi-tab Excel report with all donation data.
    """
    output = BytesIO()
    wb = Workbook()
    
    # Styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2E4057", end_color="2E4057", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    currency_format_gbp = '£#,##0.00'
    currency_format_eur = '€#,##0.00'
    date_format = 'YYYY-MM-DD'
    
    # ===== SUMMARY SHEET =====
    ws_summary = wb.active
    ws_summary.title = "Summary"
    
    # Title
    ws_summary['A1'] = f"Political Donations Report: {company_name}"
    ws_summary['A1'].font = Font(bold=True, size=16)
    ws_summary.merge_cells('A1:D1')
    
    ws_summary['A2'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ws_summary['A3'] = ""
    
    # Summary stats
    ws_summary['A4'] = "Summary by Jurisdiction"
    ws_summary['A4'].font = Font(bold=True, size=12)
    
    headers = ['Jurisdiction', 'Records Found', 'Total Value', 'Date Range']
    for col, header in enumerate(headers, 1):
        cell = ws_summary.cell(row=5, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
    
    row = 6
    
    # UK stats
    if not uk_data.empty:
        uk_total = uk_data['ValueNumeric'].sum() if 'ValueNumeric' in uk_data.columns else 0
        uk_dates = ""
        if 'AcceptedDate' in uk_data.columns:
            try:
                dates = pd.to_datetime(uk_data['AcceptedDate'], errors='coerce')
                uk_dates = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
            except:
                pass
        
        ws_summary.cell(row=row, column=1, value="UK").border = border
        ws_summary.cell(row=row, column=2, value=len(uk_data)).border = border
        cell = ws_summary.cell(row=row, column=3, value=f"£{uk_total:,.2f}")
        cell.border = border
        ws_summary.cell(row=row, column=4, value=uk_dates).border = border
        row += 1
    else:
        ws_summary.cell(row=row, column=1, value="UK").border = border
        ws_summary.cell(row=row, column=2, value=0).border = border
        ws_summary.cell(row=row, column=3, value="-").border = border
        ws_summary.cell(row=row, column=4, value="-").border = border
        row += 1
    
    # Germany stats
    if germany_data is not None and not germany_data.empty:
        de_total = germany_data['Amount'].sum() if 'Amount' in germany_data.columns else 0
        de_dates = ""
        if 'Year' in germany_data.columns:
            de_dates = f"{germany_data['Year'].min()} to {germany_data['Year'].max()}"
        
        ws_summary.cell(row=row, column=1, value="Germany").border = border
        ws_summary.cell(row=row, column=2, value=len(germany_data)).border = border
        cell = ws_summary.cell(row=row, column=3, value=f"€{de_total:,.2f}")
        cell.border = border
        ws_summary.cell(row=row, column=4, value=de_dates).border = border
        row += 1
    else:
        ws_summary.cell(row=row, column=1, value="Germany").border = border
        ws_summary.cell(row=row, column=2, value=0).border = border
        ws_summary.cell(row=row, column=3, value="-").border = border
        ws_summary.cell(row=row, column=4, value="-").border = border
        row += 1
    
    # EU stats
    if eu_data is not None and not eu_data.empty:
        eu_total = eu_data['Amount'].sum() if 'Amount' in eu_data.columns else 0
        eu_dates = ""
        if 'Year' in eu_data.columns:
            eu_dates = f"{eu_data['Year'].min()} to {eu_data['Year'].max()}"
        
        ws_summary.cell(row=row, column=1, value="EU").border = border
        ws_summary.cell(row=row, column=2, value=len(eu_data)).border = border
        cell = ws_summary.cell(row=row, column=3, value=f"€{eu_total:,.2f}")
        cell.border = border
        ws_summary.cell(row=row, column=4, value=eu_dates).border = border
        row += 1
    else:
        ws_summary.cell(row=row, column=1, value="EU").border = border
        ws_summary.cell(row=row, column=2, value=0).border = border
        ws_summary.cell(row=row, column=3, value="-").border = border
        ws_summary.cell(row=row, column=4, value="-").border = border
    
    # Adjust column widths
    ws_summary.column_dimensions['A'].width = 20
    ws_summary.column_dimensions['B'].width = 15
    ws_summary.column_dimensions['C'].width = 18
    ws_summary.column_dimensions['D'].width = 25
    
    # ===== UK DATA SHEET =====
    if not uk_data.empty:
        ws_uk = wb.create_sheet("UK - Electoral Commission")
        
        # Write headers
        for col, header in enumerate(uk_data.columns, 1):
            cell = ws_uk.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border
        
        # Write data
        for row_idx, row_data in enumerate(uk_data.values, 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws_uk.cell(row=row_idx, column=col_idx, value=value)
                cell.border = border
        
        # Adjust column widths
        for col in ws_uk.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_uk.column_dimensions[column].width = adjusted_width
    
    # ===== GERMANY DATA SHEET =====
    if germany_data is not None and not germany_data.empty:
        ws_de = wb.create_sheet("Germany - Bundestag")
        
        # Write headers
        for col, header in enumerate(germany_data.columns, 1):
            cell = ws_de.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border
        
        # Write data
        for row_idx, row_data in enumerate(germany_data.values, 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws_de.cell(row=row_idx, column=col_idx, value=value)
                cell.border = border
        
        # Adjust column widths
        for col in ws_de.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_de.column_dimensions[column].width = adjusted_width
    
    # ===== EU DATA SHEET =====
    if eu_data is not None and not eu_data.empty:
        ws_eu = wb.create_sheet("EU - APPF")
        
        # Write headers
        for col, header in enumerate(eu_data.columns, 1):
            cell = ws_eu.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border
        
        # Write data
        for row_idx, row_data in enumerate(eu_data.values, 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws_eu.cell(row=row_idx, column=col_idx, value=value)
                cell.border = border
        
        # Adjust column widths
        for col in ws_eu.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_eu.column_dimensions[column].width = adjusted_width
    
    # ===== DATA SOURCES SHEET =====
    ws_sources = wb.create_sheet("Data Sources")
    
    ws_sources['A1'] = "Data Sources & Methodology"
    ws_sources['A1'].font = Font(bold=True, size=14)
    
    source_info = [
        "",
        "UK Electoral Commission",
        f"  URL: {DATA_SOURCES['uk']['url']}",
        f"  Coverage: {DATA_SOURCES['uk']['coverage']}",
        f"  Threshold: {DATA_SOURCES['uk']['threshold']}",
        "",
        "German Bundestag",
        f"  URL: {DATA_SOURCES['germany']['url']}",
        f"  Coverage: {DATA_SOURCES['germany']['coverage']}",
        f"  Threshold: {DATA_SOURCES['germany']['threshold']}",
        "  Note: Data scraped from official Bundestag parliamentary publications",
        "",
        "EU Authority for Political Parties (APPF)",
        f"  URL: {DATA_SOURCES['eu']['url']}",
        f"  Coverage: {DATA_SOURCES['eu']['coverage']}",
        f"  Threshold: {DATA_SOURCES['eu']['threshold']}",
        "  Note: Covers European political parties (EPP, PES, ALDE, ECR, etc.)",
        "  Data from published Excel files at appf.europa.eu/appf/en/donations-and-contributions",
        "",
        "Disclaimer:",
        "This report aggregates publicly available data from official sources.",
        "Different jurisdictions have different disclosure thresholds and requirements.",
        "Results may not represent all donations made by the searched entity.",
        "",
        "EU-level parties are distinct from national parties - they are pan-European",
        "federations that coordinate policies across the European Parliament.",
    ]
    
    for row, text in enumerate(source_info, 2):
        ws_sources.cell(row=row, column=1, value=text)
    
    ws_sources.column_dimensions['A'].width = 80
    
    wb.save(output)
    output.seek(0)
    return output


# ============= MAIN INTERFACE =============

# Search input
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input(
        "Enter company or donor name",
        placeholder="e.g., JCB, Dyson, Unite the Union",
        help="Search for donations by company name, individual, or organisation"
    )

with col2:
    search_button = st.button("🔍 Search", type="primary", use_container_width=True)

# Perform search
if search_button and search_query:
    with st.spinner("Searching donation databases..."):
        # Initialize results
        all_results = {}
        
        # Search UK
        st.write("### 🇬🇧 United Kingdom")
        uk_results = search_uk_donations(search_query, search_years)
        all_results['uk'] = uk_results
        
        if not uk_results.empty:
            st.success(f"Found {len(uk_results)} donation records in UK")
            
            # Display summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                total_value = uk_results['ValueNumeric'].sum() if 'ValueNumeric' in uk_results.columns else 0
                st.metric("Total Value", f"£{total_value:,.2f}")
            with col2:
                st.metric("Number of Donations", len(uk_results))
            with col3:
                if 'RegulatedEntityName' in uk_results.columns:
                    unique_parties = uk_results['RegulatedEntityName'].nunique()
                    st.metric("Parties", unique_parties)
            
            # Display formatted table
            formatted_uk = format_uk_results(uk_results)
            st.dataframe(formatted_uk, use_container_width=True, hide_index=True)
            
            # Party breakdown
            if 'RegulatedEntityName' in uk_results.columns and 'ValueNumeric' in uk_results.columns:
                st.write("**Donations by Party:**")
                party_summary = uk_results.groupby('RegulatedEntityName').agg({
                    'ValueNumeric': ['sum', 'count']
                }).round(2)
                party_summary.columns = ['Total (£)', 'Count']
                party_summary = party_summary.sort_values('Total (£)', ascending=False)
                st.dataframe(party_summary, use_container_width=True)
        else:
            st.info("No UK donation records found for this search term.")
        
        st.divider()
        
        # Search Germany
        st.write("### 🇩🇪 Germany")
        with st.spinner("Scraping Bundestag donations data..."):
            germany_results = search_germany_donations(search_query, search_years)
        all_results['germany'] = germany_results
        
        if not germany_results.empty:
            st.success(f"Found {len(germany_results)} donation records in Germany")
            
            # Display summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                total_value = germany_results['Amount'].sum()
                st.metric("Total Value", f"€{total_value:,.2f}")
            with col2:
                st.metric("Number of Donations", len(germany_results))
            with col3:
                unique_parties = germany_results['Party'].nunique()
                st.metric("Parties", unique_parties)
            
            # Display formatted table
            formatted_de = format_germany_results(germany_results)
            st.dataframe(formatted_de, use_container_width=True, hide_index=True)
            
            # Party breakdown
            if 'Party' in germany_results.columns:
                st.write("**Donations by Party:**")
                party_summary = germany_results.groupby('Party').agg({
                    'Amount': ['sum', 'count']
                }).round(2)
                party_summary.columns = ['Total (€)', 'Count']
                party_summary = party_summary.sort_values('Total (€)', ascending=False)
                st.dataframe(party_summary, use_container_width=True)
        else:
            st.info("No German donation records found for this search term.")
        
        st.caption("**Note:** German data covers large donations >€35,000 (since March 2024) or >€50,000 (before March 2024).")
        
        st.divider()
        
        # Search EU
        st.write("### 🇪🇺 European Union")
        with st.spinner("Downloading EU APPF donations data..."):
            eu_results = search_eu_donations(search_query)
        all_results['eu'] = eu_results
        
        if not eu_results.empty:
            st.success(f"Found {len(eu_results)} donation records at EU level")
            
            # Display summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                total_value = eu_results['Amount'].sum()
                st.metric("Total Value", f"€{total_value:,.2f}")
            with col2:
                st.metric("Number of Donations", len(eu_results))
            with col3:
                unique_parties = eu_results['Party'].nunique()
                st.metric("EU Parties", unique_parties)
            
            # Display formatted table
            formatted_eu = format_eu_results(eu_results)
            st.dataframe(formatted_eu, use_container_width=True, hide_index=True)
            
            # Party breakdown
            if 'Party' in eu_results.columns:
                st.write("**Donations by EU Party:**")
                party_summary = eu_results.groupby('Party').agg({
                    'Amount': ['sum', 'count']
                }).round(2)
                party_summary.columns = ['Total (€)', 'Count']
                party_summary = party_summary.sort_values('Total (€)', ascending=False)
                st.dataframe(party_summary, use_container_width=True)
        else:
            st.info("No EU-level donation records found for this search term.")
        
        st.caption("**Note:** EU data covers donations to European political parties (e.g., EPP, PES, ALDE). Threshold: €12,000 for immediate disclosure.")
        
        st.divider()
        
        # Export section
        st.write("### 📥 Export Results")
        
        # Generate Excel
        excel_file = create_excel_report(search_query, uk_results, germany_results, eu_results)
        
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_file,
            file_name=f"donations_{search_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        
        st.caption("Excel report includes all raw data, summary statistics, and source documentation.")

elif search_button:
    st.warning("Please enter a search term.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    Data sourced from official electoral commission databases. 
    For research and journalistic purposes.
</div>
""", unsafe_allow_html=True)
