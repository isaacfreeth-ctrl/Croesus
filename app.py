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


# ============= GERMANY (via Bundestag published data) =============

def search_germany_donations(query: str, years: int = 5) -> pd.DataFrame:
    """
    Search German party donations.
    Note: Germany publishes large donations (>€35K) on Bundestag website.
    This function scrapes available structured data.
    """
    # The Bundestag publishes donation data but not via a clean API
    # DonationWatch aggregates this data - we'll note this for the user
    
    # For now, return placeholder with instructions
    # In production, this would scrape bundestag.de or use DonationWatch data
    
    st.info("""
    **Germany:** Large donations (>€35,000) are published by the Bundestag.
    For comprehensive German data, also check [DonationWatch](https://donation.watch/en/germany).
    """)
    
    return pd.DataFrame()


# ============= EU LEVEL (APPF) =============

def search_eu_donations(query: str) -> pd.DataFrame:
    """
    Search EU Authority for Political Parties and Foundations.
    """
    # APPF publishes donation data but access method needs verification
    # For now, provide guidance
    
    st.info("""
    **EU Level:** The Authority for European Political Parties publishes donation data.
    Check [APPF Donations](https://www.appf.europa.eu/appf/en/donations-and-contributions).
    """)
    
    return pd.DataFrame()


# ============= EXCEL EXPORT =============

def create_excel_report(company_name: str, uk_data: pd.DataFrame) -> BytesIO:
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
    currency_format = '£#,##0.00'
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
        cell = ws_summary.cell(row=row, column=3, value=uk_total)
        cell.number_format = currency_format
        cell.border = border
        ws_summary.cell(row=row, column=4, value=uk_dates).border = border
        row += 1
    else:
        ws_summary.cell(row=row, column=1, value="UK").border = border
        ws_summary.cell(row=row, column=2, value=0).border = border
        ws_summary.cell(row=row, column=3, value="-").border = border
        ws_summary.cell(row=row, column=4, value="-").border = border
        row += 1
    
    # Germany placeholder
    ws_summary.cell(row=row, column=1, value="Germany").border = border
    ws_summary.cell(row=row, column=2, value="See DonationWatch").border = border
    ws_summary.cell(row=row, column=3, value="-").border = border
    ws_summary.cell(row=row, column=4, value="-").border = border
    row += 1
    
    # EU placeholder
    ws_summary.cell(row=row, column=1, value="EU").border = border
    ws_summary.cell(row=row, column=2, value="See APPF").border = border
    ws_summary.cell(row=row, column=3, value="-").border = border
    ws_summary.cell(row=row, column=4, value="-").border = border
    
    # Adjust column widths
    ws_summary.column_dimensions['A'].width = 20
    ws_summary.column_dimensions['B'].width = 15
    ws_summary.column_dimensions['C'].width = 15
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
        "  Note: For aggregated data, see https://donation.watch/en/germany",
        "",
        "EU Authority for Political Parties",
        f"  URL: {DATA_SOURCES['eu']['url']}",
        f"  Coverage: {DATA_SOURCES['eu']['coverage']}",
        f"  Threshold: {DATA_SOURCES['eu']['threshold']}",
        "",
        "Disclaimer:",
        "This report aggregates publicly available data from official sources.",
        "Different jurisdictions have different disclosure thresholds and requirements.",
        "Results may not represent all donations made by the searched entity.",
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
        
        # Search Germany (placeholder)
        st.write("### 🇩🇪 Germany")
        germany_results = search_germany_donations(search_query, search_years)
        all_results['germany'] = germany_results
        
        st.divider()
        
        # Search EU (placeholder)
        st.write("### 🇪🇺 European Union")
        eu_results = search_eu_donations(search_query)
        all_results['eu'] = eu_results
        
        st.divider()
        
        # Export section
        st.write("### 📥 Export Results")
        
        # Generate Excel
        excel_file = create_excel_report(search_query, uk_results)
        
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
