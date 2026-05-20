import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def main():
    print("Step 1: Loading intermediate datasets...")
    # Load intermediate datasets
    ppi_df = pd.read_csv('ppi_energy.csv')
    carbon_df = pd.read_csv('carbon_trends.csv')
    
    # Fill NaN values in investment with 0 for aggregation
    ppi_df['investment_pp_clean'] = ppi_df['investment_pp'].fillna(0)
    
    print("Step 2: Performing Initial Grouping...")
    # Earliest policy start year per country
    policy_map = carbon_df.groupby('jurisdiction')['start_year'].min().to_dict()
    
    # Total PPI footprint countries
    ppi_countries = sorted(ppi_df['country'].unique())
    
    initial_groups = {}
    for country in ppi_countries:
        st_year = policy_map.get(country)
        if st_year is None:
            initial_groups[country] = {
                'initial_group': 'Control',
                'start_year': None,
                'exclusion_reason': None
            }
        else:
            if 2011 <= st_year <= 2023:
                initial_groups[country] = {
                    'initial_group': 'Treatment',
                    'start_year': st_year,
                    'exclusion_reason': None
                }
            else:
                initial_groups[country] = {
                    'initial_group': 'Excluded',
                    'start_year': st_year,
                    'exclusion_reason': f"Policy start year ({st_year}) is outside the [2011, 2023] window"
                }
                
    print("Step 3: Applying Sample Density Check...")
    # For each treated country, verify the density check
    final_groups = {}
    treatment_countries = []
    
    for country, info in initial_groups.items():
        if info['initial_group'] == 'Treatment':
            T = info['start_year']
            # Pre-treatment projects: [T - 5, T - 1]
            pre_proj = ppi_df[(ppi_df['country'] == country) & (ppi_df['year'] >= T - 5) & (ppi_df['year'] <= T - 1)]
            pre_count = len(pre_proj)
            
            # Post-treatment projects: [T, T + 3]
            post_proj = ppi_df[(ppi_df['country'] == country) & (ppi_df['year'] >= T) & (ppi_df['year'] <= T + 3)]
            post_count = len(post_proj)
            
            if pre_count >= 1 and post_count >= 1:
                final_groups[country] = {
                    'group': 'Treatment',
                    'start_year': T,
                    'exclusion_reason': None
                }
                treatment_countries.append((country, T))
            else:
                reason = []
                if pre_count == 0:
                    reason.append(f"Insufficient pre-treatment project density (0 projects in [{T-5}, {T-1}])")
                if post_count == 0:
                    reason.append(f"Insufficient post-treatment project density (0 projects in [{T}, {T+3}])")
                
                final_groups[country] = {
                    'group': 'Excluded',
                    'start_year': T,
                    'exclusion_reason': " and ".join(reason)
                }
        else:
            final_groups[country] = {
                'group': info['initial_group'],
                'start_year': info['start_year'],
                'exclusion_reason': info['exclusion_reason']
            }
            
    # Print country classifications
    print("\n=== Final Country Classifications ===")
    treat_list = []
    control_list = []
    excluded_list = []
    
    for country in sorted(ppi_countries):
        grp = final_groups[country]['group']
        yr = final_groups[country]['start_year']
        reason = final_groups[country]['exclusion_reason']
        if grp == 'Treatment':
            treat_list.append(country)
            print(f"Country: {country} | Group: Treatment | Start Year: {yr}")
        elif grp == 'Control':
            control_list.append(country)
        else:
            excluded_list.append(country)
            print(f"Country: {country} | Group: Excluded | Start Year: {yr} | Reason: {reason}")
            
    print(f"\nSummary Counts: Treatment: {len(treat_list)}, Control: {len(control_list)}, Excluded: {len(excluded_list)}")
    
    # Average treatment year of final treated group
    mean_tx_year = np.mean([yr for c, yr in treatment_countries])
    pseudo_tx_year = int(round(mean_tx_year))
    print(f"Average Treatment Year of Treated Group: {mean_tx_year:.2f} (Rounded to {pseudo_tx_year})")
    
    print("\nStep 4: Generating Overlap Summary Matrix...")
    # Calculate totals by group
    # We aggregate total investment and project counts from 2010-2024
    ppi_grouped_list = []
    for country in ppi_countries:
        grp = final_groups[country]['group']
        # Filter ppi data for 2010-2024
        country_ppi = ppi_df[(ppi_df['country'] == country) & (ppi_df['year'] >= 2010) & (ppi_df['year'] <= 2024)]
        inv_sum = country_ppi['investment_pp_clean'].sum()
        proj_count = len(country_ppi)
        
        ppi_grouped_list.append({
            'country': country,
            'group': grp,
            'investment': inv_sum,
            'projects': proj_count
        })
        
    df_grouped = pd.DataFrame(ppi_grouped_list)
    
    # We only summarize Treatment vs Control
    matrix_data = []
    for g in ['Treatment', 'Control']:
        sub_df = df_grouped[df_grouped['group'] == g]
        matrix_data.append({
            'Group': f"{g} Group",
            'Number of Countries': len(sub_df),
            'Total Investment ($USD)': sub_df['investment'].sum(),
            'Total Projects': sub_df['projects'].sum()
        })
        
    df_matrix = pd.DataFrame(matrix_data)
    
    print("\n" + "="*60)
    print("                   OVERLAP SUMMARY MATRIX")
    print("="*60)
    # Format for printing
    for idx, r in df_matrix.iterrows():
        print(f"Group:                  {r['Group']}")
        print(f"Number of Countries:    {r['Number of Countries']}")
        print(f"Total Investment:       ${r['Total Investment ($USD)']:,.2f} USD")
        print(f"Total Projects:         {r['Total Projects']}")
        print("-" * 60)
        
    # Also save the matrix as a CSV for diagnostic records
    df_matrix.to_csv('overlap_summary_matrix.csv', index=False)
    
    print("Step 5: Generating Timeline Alignment Plot...")
    # Order treated countries by start year
    treatment_countries_sorted = sorted(treatment_countries, key=lambda x: x[1])
    treated_names = [c for c, yr in treatment_countries_sorted]
    treated_years = [yr for c, yr in treatment_countries_sorted]
    
    # Create the figure
    plt.rcParams.update({'font.size': 11, 'font.family': 'sans-serif'})
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    
    # Background color theme (sleek off-white/light gray)
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#ffffff')
    
    # Plot timelines
    y_ticks = []
    for idx, (country, T) in enumerate(treatment_countries_sorted):
        y_val = idx + 1
        y_ticks.append(y_val)
        
        # Draw pre-treatment window (T-5 to T-1)
        ax.axhspan(y_val - 0.2, y_val + 0.2, xmin=(T-5 - 2010)/14, xmax=(T-1 - 2010)/14, 
                   color='#c5d9f1', alpha=0.4, label='Pre-Treatment Window' if idx == 0 else "")
        # Draw post-treatment window (T to T+3)
        ax.axhspan(y_val - 0.2, y_val + 0.2, xmin=(T - 2010)/14, xmax=(min(T+3, 2024) - 2010)/14, 
                   color='#f2dcdb', alpha=0.4, label='Post-Treatment Window' if idx == 0 else "")
        
        # Plot horizontal base line
        ax.plot([2010, 2024], [y_val, y_val], color='#e0e0e0', linestyle='-', linewidth=1.5, zorder=1)
        
        # Plot annual project counts as scatter points
        for yr in range(2010, 2025):
            proj_yr = ppi_df[(ppi_df['country'] == country) & (ppi_df['year'] == yr)]
            count = len(proj_yr)
            if count > 0:
                # Scale marker size based on project count
                marker_size = 40 + count * 15
                # Color code points by investment volume
                inv_m = proj_yr['investment_pp_clean'].sum() / 1_000_000
                sc = ax.scatter(yr, y_val, s=marker_size, c=inv_m, cmap='viridis', vmin=0, vmax=2000, 
                                edgecolors='#333333', linewidths=0.8, zorder=3)
                
                # Label project count on top of the point if it's substantial
                ax.annotate(str(count), (yr, y_val), textcoords="offset points", xytext=(0,-4), 
                            ha='center', fontsize=8, color='white' if inv_m < 800 else 'black', weight='bold', zorder=4)
        
        # Plot treatment start year marker
        ax.scatter(T, y_val, marker='*', s=350, color='#d9534f', edgecolors='black', linewidths=1.0, zorder=5, 
                   label='Policy Start Year' if idx == 0 else "")
        
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(treated_names, fontweight='bold')
    ax.set_xlim(2009.5, 2024.5)
    ax.set_ylim(0.5, len(treated_names) + 0.5)
    ax.set_xlabel("Year", fontweight='bold', labelpad=10)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_title("Timeline Alignment and Project Overlap for Treated Countries (2010–2024)", 
                 fontsize=14, fontweight='bold', pad=15)
    
    # Custom legend
    handles, labels = ax.get_legend_handles_labels()
    # Add a scatter size legend entry manually
    import matplotlib.lines as mlines
    star = mlines.Line2D([], [], color='#d9534f', marker='*', linestyle='None', markersize=15, 
                         markeredgecolor='black', label='Policy Start Year (t=0)')
    blue_patch = plt.Rectangle((0, 0), 1, 1, fc='#c5d9f1', alpha=0.6, label='Pre-Treatment Window (t-5 to t-1)')
    red_patch = plt.Rectangle((0, 0), 1, 1, fc='#f2dcdb', alpha=0.6, label='Post-Treatment Window (t to t+3)')
    
    # Colormap colorbar
    # Create colormap axes
    cbar = plt.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(0, 2000), cmap='viridis'), 
                        ax=ax, orientation='horizontal', pad=0.15, shrink=0.6)
    cbar.set_label("Annual Energy Investment (USD Millions)", fontweight='bold', fontsize=10)
    
    plt.tight_layout()
    leg = ax.legend(handles=[star, blue_patch, red_patch], loc='upper left', bbox_to_anchor=(1.02, 1.0),
                    frameon=True, facecolor='#ffffff', edgecolor='#e0e0e0')
    
    plt.savefig('timeline_alignment.png', dpi=300, facecolor=fig.get_facecolor(), bbox_extra_artists=(leg,), bbox_inches='tight')
    plt.close()
    print("Saved Timeline Alignment Plot as timeline_alignment.png")
    
    print("Step 6: Generating Naive Trend Plot...")
    # We calculate average annual investment for Treatment vs Control relative to policy start year
    # Relative event year range: -5 to +3
    relative_years = list(range(-5, 4))
    
    treatment_investment_rel = {ry: [] for ry in relative_years}
    control_investment_rel = {ry: [] for ry in relative_years}
    
    # For each treated country, calculate annual investment for relative years
    for country, T in treatment_countries:
        for ry in relative_years:
            yr = T + ry
            # Get investment in USD Millions
            val = ppi_df[(ppi_df['country'] == country) & (ppi_df['year'] == yr)]['investment_pp_clean'].sum() / 1_000_000
            treatment_investment_rel[ry].append(val)
            
    # For each control country, use pseudo-treatment year (2018) to calculate relative years
    for country in control_list:
        for ry in relative_years:
            yr = pseudo_tx_year + ry
            val = ppi_df[(ppi_df['country'] == country) & (ppi_df['year'] == yr)]['investment_pp_clean'].sum() / 1_000_000
            control_investment_rel[ry].append(val)
            
    # Compute averages across countries in each group
    avg_treat_inv = [np.mean(treatment_investment_rel[ry]) for ry in relative_years]
    avg_control_inv = [np.mean(control_investment_rel[ry]) for ry in relative_years]
    
    # Standard errors for error bars (optional, but shows scientific rigor)
    se_treat_inv = [np.std(treatment_investment_rel[ry]) / np.sqrt(len(treatment_countries)) for ry in relative_years]
    se_control_inv = [np.std(control_investment_rel[ry]) / np.sqrt(len(control_list)) for ry in relative_years]
    
    # Plot Naive Trend Plot
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#ffffff')
    
    # Draw gridlines
    ax.grid(color='#e5e5e5', linestyle='--', linewidth=0.8, zorder=1)
    
    # Plot Treatment Group Line
    ax.errorbar(relative_years, avg_treat_inv, yerr=se_treat_inv, fmt='-o', color='#d9534f', linewidth=2.5, 
                markersize=8, elinewidth=1.5, capsize=4, capthick=1.5, label='Treatment Group (Active Carbon Policy)', zorder=3)
                
    # Plot Control Group Line
    ax.errorbar(relative_years, avg_control_inv, yerr=se_control_inv, fmt='-s', color='#4b6b94', linewidth=2.5, 
                markersize=8, elinewidth=1.5, capsize=4, capthick=1.5, label=f'Control Group (No Policy, Pseudo-T={pseudo_tx_year})', zorder=2)
                
    # Highlight relative event sections
    ax.axvspan(-5, -1, color='#c5d9f1', alpha=0.2, label='Pre-Treatment Window')
    ax.axvspan(0, 3, color='#f2dcdb', alpha=0.2, label='Post-Treatment Window')
    
    # Vertical line at t=0
    ax.axvline(0, color='#333333', linestyle='--', linewidth=2.0, zorder=4)
    ax.text(0.1, max(max(avg_treat_inv), max(avg_control_inv)) * 0.9, 'Policy Implementation (t=0)', 
            fontsize=10, fontweight='bold', rotation=0, color='#333333')
            
    ax.set_xlim(-5.5, 3.5)
    ax.set_xticks(relative_years)
    ax.set_xticklabels([f"t{ry}" if ry < 0 else f"t+{ry}" if ry > 0 else "t=0" for ry in relative_years], fontweight='bold')
    
    ax.set_xlabel("Relative Event Time (Years from Policy Implementation)", fontweight='bold', labelpad=10)
    ax.set_ylabel("Average Annual Energy Investment per Country (USD Millions)", fontweight='bold', labelpad=10)
    ax.set_title("Naive Comparison of Energy Investment Trends (Treatment vs. Control)", 
                 fontsize=13, fontweight='bold', pad=15)
                 
    ax.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#e0e0e0')
    
    plt.tight_layout()
    plt.savefig('naive_trend.png', dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print("Saved Naive Trend Plot as naive_trend.png")
    
    print("\nAll tasks completed successfully!")

if __name__ == '__main__':
    main()
