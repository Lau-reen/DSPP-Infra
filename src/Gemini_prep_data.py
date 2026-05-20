import pandas as pd
import numpy as np

# Define standard ISO 3-digit country code mapping
iso3_map = {
    # PPI Countries
    'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Angola': 'AGO', 'Argentina': 'ARG',
    'Armenia': 'ARM', 'Azerbaijan': 'AZE', 'Bangladesh': 'BGD', 'Belarus': 'BLR', 'Benin': 'BEN',
    'Bosnia and Herzegovina': 'BIH', 'Botswana': 'BWA', 'Brazil': 'BRA', 'Bulgaria': 'BGR',
    'Burkina Faso': 'BFA', 'Burundi': 'BDI', 'Cabo Verde': 'CPV', 'Cambodia': 'KHM', 'Cameroon': 'CMR',
    'Chad': 'TCD', 'China': 'CHN', 'Colombia': 'COL', 'Congo, Dem. Rep.': 'COD', 'Costa Rica': 'CRI',
    "Côte d'Ivoire": 'CIV', "C\x92te d'Ivoire": 'CIV', "Cte d'Ivoire": 'CIV', "Côte d’Ivoire": 'CIV',
    'Djibouti': 'DJI', 'Dominican Republic': 'DOM', 'Ecuador': 'ECU', 'Egypt, Arab Rep.': 'EGY',
    'El Salvador': 'SLV', 'Eswatini': 'SWZ', 'Ethiopia': 'ETH', 'Gabon': 'GAB', 'Georgia': 'GEO',
    'Ghana': 'GHA', 'Guatemala': 'GTM', 'Guinea': 'GIN', 'Honduras': 'HND', 'India': 'IND',
    'Indonesia': 'IDN', 'Iran, Islamic Rep.': 'IRN', 'Iraq': 'IRQ', 'Jamaica': 'JAM', 'Jordan': 'JOR',
    'Kazakhstan': 'KAZ', 'Kenya': 'KEN', 'Kosovo': 'XKX', 'Kyrgyz Republic': 'KGZ', 'Lao PDR': 'LAO',
    'Lebanon': 'LBN', 'Lesotho': 'LSO', 'Liberia': 'LBR', 'Madagascar': 'MDG', 'Malawi': 'MWI',
    'Malaysia': 'MYS', 'Maldives': 'MDV', 'Mali': 'MLI', 'Mauritius': 'MUS', 'Mexico': 'MEX',
    'Mongolia': 'MNG', 'Montenegro': 'MNE', 'Morocco': 'MAR', 'Mozambique': 'MOZ', 'Myanmar': 'MMR',
    'Namibia': 'NAM', 'Nepal': 'NPL', 'Nicaragua': 'NIC', 'Nigeria': 'NGA', 'North Macedonia': 'MKD',
    'Pakistan': 'PAK', 'Palau': 'PLW', 'Papua New Guinea': 'PNG', 'Peru': 'PER', 'Philippines': 'PHL',
    'Russian Federation': 'RUS', 'Rwanda': 'RWA', 'Senegal': 'SEN', 'Serbia': 'SRB', 'Serbia ': 'SRB',
    'Sierra Leone': 'SLE', 'Solomon Islands': 'SLB', 'Somalia': 'SOM', 'South Africa': 'ZAF',
    'South Sudan': 'SSD', 'Sri Lanka': 'LKA', 'St. Kitts and Nevis': 'KNA', 'St. Lucia': 'LCA',
    'St. Vincent and the Grenadines': 'VCT', 'São Tomé and Principe': 'STP', 'Tanzania': 'TZA',
    'Thailand': 'THA', 'Togo': 'TGO', 'Tonga': 'TON', 'Tunisia': 'TUN', 'Turkey': 'TUR',
    'Uganda': 'UGA', 'Ukraine': 'UKR', 'Uzbekistan': 'UZB', 'Vietnam': 'VNM', 'Viet Nam': 'VNM',
    'Zambia': 'ZMB', 'Zimbabwe': 'ZWE',
    
    # Carbon pricing specific jurisdictions
    'Andorra': 'AND', 'Australia': 'AUS', 'Austria': 'AUT', 'Bahrain': 'BHR', 'Brunei Darussalam': 'BRN',
    'Canada': 'CAN', 'Chile': 'CHL', 'Denmark': 'DNK', 'Estonia': 'EST', 'Finland': 'FIN',
    'France': 'FRA', 'Germany': 'DEU', 'Iceland': 'ISL', 'Ireland': 'IRL', 'Israel': 'ISR',
    'Japan': 'JPN', 'Korea': 'KOR', 'Korea, Rep.': 'KOR', 'Latvia': 'LVA', 'Liechtenstein': 'LIE',
    'Luxembourg': 'LUX', 'Netherlands': 'NLD', 'New Zealand': 'NZL', 'Norway': 'NOR', 'Poland': 'POL',
    'Portugal': 'PRT', 'Singapore': 'SGP', 'Slovenia': 'SVN', 'Spain': 'ESP', 'Sweden': 'SWE',
    'Switzerland': 'CHE', 'United Kingdom': 'GBR', 'Uruguay': 'URY',
    'EU27+': 'EU27', 'RGGI': 'RGGI'
}

def clean_str(s):
    if not isinstance(s, str):
        return s
    return s.strip().replace('\xa0', '')

def main():
    print("Step 1: Loading raw datasets...")
    # Load World Bank PPI Energy Dataset
    ppi_xl = pd.ExcelFile('WB_PPI_2010-2024_energy.xlsx')
    ppi_df = pd.read_excel(ppi_xl, sheet_name='CustomQuery')
    
    # Load Carbon Pricing Dashboard Dataset
    carbon_xl = pd.ExcelFile('WB_carbon_pricing.xlsx')
    df_info = pd.read_excel(carbon_xl, sheet_name='Compliance_Gen Info', header=4)
    df_price = pd.read_excel(carbon_xl, sheet_name='Compliance_Price', header=1)
    df_em = pd.read_excel(carbon_xl, sheet_name='Compliance_Emissions', header=2)
    
    print("Step 2: Processing PPI Dataset...")
    # Filter PPI dataset strictly for 'Energy' sector and years 2010 to 2024
    ppi_df['Primary sector'] = ppi_df['Primary sector'].apply(clean_str)
    ppi_df['Country'] = ppi_df['Country'].apply(clean_str)
    
    # Check if there are any missing country codes
    ppi_df['country'] = ppi_df['Country'].map(iso3_map)
    missing_ppi = ppi_df[ppi_df['country'].isnull()]['Country'].unique()
    if len(missing_ppi) > 0:
        print(f"Warning: Missing ISO3 code for PPI countries: {missing_ppi}")
        
    # We use 'Financial closure year' as the timeline variable
    ppi_df['year'] = ppi_df['Financial closure year']
    
    # Parse TotalInvestment to numeric, replace 'Not Available' with NaN
    # Then multiply by 1,000,000 to convert to USD (since database represents values in millions)
    ppi_df['investment_pp'] = pd.to_numeric(ppi_df['TotalInvestment'], errors='coerce') * 1_000_000
    ppi_df['technology'] = ppi_df['Technology'].apply(clean_str)
    
    # Strict filtering
    ppi_filtered = ppi_df[
        (ppi_df['Primary sector'] == 'Energy') &
        (ppi_df['year'] >= 2010) &
        (ppi_df['year'] <= 2024)
    ].copy()
    
    # Keep only required columns
    ppi_out = ppi_filtered[['country', 'year', 'investment_pp', 'technology']]
    
    # Export to ppi_energy.csv
    ppi_out.to_csv('ppi_energy.csv', index=False)
    print(f"Saved {len(ppi_out)} PPI records to ppi_energy.csv")
    
    print("Step 3: Processing Carbon Pricing Dataset...")
    # Clean names
    df_info['Jurisdiction covered'] = df_info['Jurisdiction covered'].apply(clean_str)
    df_info['Instrument name'] = df_info['Instrument name'].apply(clean_str)
    df_price['Name of the initiative'] = df_price['Name of the initiative'].apply(clean_str)
    df_em['Name of the initiative'] = df_em['Name of the initiative'].apply(clean_str)
    
    # Get active years for pricing
    year_cols_p = [c for c in df_price.columns if isinstance(c, int)]
    price_start = {}
    for idx, row in df_price.iterrows():
        uid = row['Unique ID']
        prices = row[year_cols_p].dropna()
        active = prices[prices > 0].index.tolist()
        price_start[uid] = min(active) if active else None
        
    # Get active years for emissions
    year_cols_e = [c for c in df_em.columns if isinstance(c, int)]
    em_start = {}
    for idx, row in df_em.iterrows():
        name = clean_str(row['Name of the initiative'])
        em = row[year_cols_e].dropna()
        active = em[em > 0].index.tolist()
        em_start[name] = min(active) if active else None
        
    # Manual overrides for known policy start years to handle reporting lags:
    # - Ukraine carbon tax started in 2011
    # - Kazakhstan ETS started in 2013
    # - Mexico carbon tax started in 2014
    # - Montenegro ETS started in 2020
    # - Indonesia ETS started in 2023
    # - Albania carbon tax started in 2024
    overrides = {
        'UKR': 2011,
        'KAZ': 2013,
        'MEX': 2014,
        'MNE': 2020,
        'IDN': 2023,
        'ALB': 2024
    }
    
    carbon_records = []
    for idx, row in df_info.iterrows():
        uid = row['Unique ID']
        name = clean_str(row['Instrument name'])
        itype = row['Type']
        status = row['Status']
        jur = clean_str(row['Jurisdiction covered'])
        
        iso = iso3_map.get(jur)
        if pd.isnull(iso) or iso in ['EU27', 'RGGI']:
            # Skip supranational blocks and subnational states
            continue
            
        # We only look at active national initiatives (Status must be Implemented or Abolished)
        if status not in ['Implemented', 'Abolished']:
            continue
            
        p_yr = price_start.get(uid)
        e_yr = em_start.get(name)
        possible_years = [y for y in [p_yr, e_yr] if y is not None]
        
        start_year = min(possible_years) if possible_years else None
        
        # Apply overrides
        if iso in overrides:
            start_year = overrides[iso]
            
        if start_year is not None and start_year <= 2024:
            carbon_records.append({
                'jurisdiction': iso,
                'type': itype,
                'start_year': int(start_year)
            })
            
    df_carbon_out = pd.DataFrame(carbon_records)
    
    # Export to carbon_trends.csv
    df_carbon_out.to_csv('carbon_trends.csv', index=False)
    print(f"Saved {len(df_carbon_out)} carbon policy records to carbon_trends.csv")
    print("Data preparation complete.")

if __name__ == '__main__':
    main()
