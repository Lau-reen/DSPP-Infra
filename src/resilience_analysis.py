import os
import re
import pandas as pd
import numpy as np

def parse_pattern_to_regex(pattern_str):
    # Split by alternative OR
    alternatives = [alt.strip() for alt in pattern_str.split(" OR ")]
    regex_parts = []
    for alt in alternatives:
        words = alt.split()
        word_patterns = []
        for word in words:
            # Escape regex characters but keep '*'
            escaped = re.escape(word).replace(r'\*', '*')
            # Replace '*' with '\w*'
            regex_word = escaped.replace('*', r'\w*')
            word_patterns.append(regex_word)
        
        alt_pattern = r'\s+'.join(word_patterns)
        # Apply word boundaries at the start and end
        regex_parts.append(rf"\b{alt_pattern}\b")
    
    return "|".join(regex_parts)

def main():
    print("Step 1: Loading and parsing taxonomy...")
    taxonomy_path = "c:/Users/laure/Documents/DSPP_local/mentges_ci_enhanced_climate_resilience_taxonomy.csv"
    taxonomy = pd.read_csv(taxonomy_path)
    
    # Prune taxonomy to focus strictly on infrastructure resilience
    exclude_terms = {
        'Mitigation',
        'Climate adaptation',
        'Climate resilience',
        'Do no significant harm (DNSH)',
        'Maladaptation',
        'Stranded assets',
        'Resilient Agrifood Systems',
        'Resilient Health',
        'Resilient Social Systems',
        'Social resilience',
        'Economic resilience'
    }
    original_count = len(taxonomy)
    taxonomy = taxonomy[~taxonomy['Term'].isin(exclude_terms)].copy()
    print(f"Loaded {original_count} taxonomy terms. Pruned {original_count - len(taxonomy)} terms. Keeping {len(taxonomy)} terms for infrastructure resilience.")
    
    # Parse patterns into regexes
    taxonomy['Compiled_Regex'] = taxonomy['Search_Pattern'].apply(parse_pattern_to_regex)
    
    # Test example
    example_row = taxonomy[taxonomy['Term'] == 'Climate Risk Assessment']
    if not example_row.empty:
        print(f"Test pattern conversion for 'Climate Risk Assessment':")
        print(f"  Pattern: {example_row['Search_Pattern'].values[0]}")
        print(f"  Regex:   {example_row['Compiled_Regex'].values[0]}")

    print("\nStep 2: Loading CPDB dataset...")
    cpdb_path = "c:/Users/laure/Documents/DSPP_local/cpdb_country_all.csv"
    cpdb = pd.read_csv(cpdb_path)
    print(f"Loaded CPDB dataset with {len(cpdb)} rows.")
    
    print("\nStep 3: Filtering CPDB dataset...")
    # Jurisdiction filter
    if 'National' in cpdb['jurisdiction'].unique():
        df_filtered = cpdb[cpdb['jurisdiction'] == 'National'].copy()
    else:
        df_filtered = cpdb[cpdb['jurisdiction'] == 'Country'].copy()
    print(f"After jurisdiction filter: {len(df_filtered)} rows.")
    
    # Status filter
    df_filtered = df_filtered[df_filtered['policy_status'] == 'In force'].copy()
    print(f"After status filter ('In force'): {len(df_filtered)} rows.")
    
    # Time horizon filter
    df_filtered['start_date'] = pd.to_numeric(df_filtered['start_date'], errors='coerce')
    df_filtered['end_date'] = pd.to_numeric(df_filtered['end_date'], errors='coerce')
    
    cond_start = df_filtered['start_date'].isna() | (df_filtered['start_date'] <= 2024)
    cond_end = df_filtered['end_date'].isna() | (df_filtered['end_date'] >= 2014)
    df_filtered = df_filtered[cond_start & cond_end].copy()
    print(f"After time horizon (2014-2024) filter: {len(df_filtered)} rows.")
    
    print("\nStep 4: Performing keyword matching...")
    # Combine text fields (NaN-safe)
    df_filtered['policy_description'] = df_filtered['policy_description'].fillna("")
    df_filtered['policy_objective'] = df_filtered['policy_objective'].fillna("")
    df_filtered['combined_text'] = df_filtered['policy_description'] + " " + df_filtered['policy_objective']
    
    # Precompile regexes for performance
    compiled_rules = []
    for idx, row in taxonomy.iterrows():
        try:
            pattern = re.compile(row['Compiled_Regex'], re.IGNORECASE)
            compiled_rules.append((row['Term'], row['Category'], pattern))
        except re.error as e:
            print(f"Regex error compiling pattern for {row['Term']}: {e}")
            
    resilience_flags = []
    matching_metadata_list = []
    
    # Track statistics for matches
    term_match_counts = {}
    
    for idx, row in df_filtered.iterrows():
        text = row['combined_text']
        matched_terms = []
        for term, cat, pattern in compiled_rules:
            if pattern.search(text):
                matched_terms.append(f"{term} ({cat})")
                term_match_counts[f"{term} ({cat})"] = term_match_counts.get(f"{term} ({cat})", 0) + 1
        
        if matched_terms:
            resilience_flags.append(1)
            matching_metadata_list.append("; ".join(matched_terms))
        else:
            resilience_flags.append(0)
            matching_metadata_list.append("")
            
    df_filtered['resilience'] = resilience_flags
    df_filtered['matching_metadata'] = matching_metadata_list
    
    print("\nStep 5: Deduplicating and Aggregating policies...")
    # We want to ensure no duplicate policies are counted for a single country.
    # Group by unique policy identifier (policy_id) to aggregate matches.
    # Since CPDB can have multiple rows per policy_id, we aggregate them first.
    def agg_policy(group):
        resilience_val = group['resilience'].max()
        # Union of matching terms
        terms_set = set()
        for val in group['matching_metadata']:
            if val:
                terms_set.update([t.strip() for t in val.split(";")])
        matching_metadata_val = "; ".join(sorted(terms_set)) if terms_set else ""
        
        # Keep the first metadata value for other columns
        first_row = group.iloc[0]
        res = first_row.copy()
        res['resilience'] = resilience_val
        res['matching_metadata'] = matching_metadata_val
        return res
        
    df_unique_policies = df_filtered.groupby('policy_id', as_index=False).apply(agg_policy)
    # Reset columns
    df_unique_policies = df_unique_policies.reset_index(drop=True)
    print(f"Deduplicated to {len(df_unique_policies)} unique policies.")
    
    # Save cpdb_resilience_annotated.csv
    df_unique_policies.to_csv("c:/Users/laure/Documents/DSPP_local/cpdb_resilience_annotated.csv", index=False)
    print("Exported cpdb_resilience_annotated.csv.")
    
    # Generate country_resilience_scores.csv
    # country_iso, country, resilience_score, policy_count
    country_groups = df_unique_policies.groupby(['country_iso', 'country'])
    
    summary_rows = []
    for (iso, country_name), group in country_groups:
        resilience_score = int(group['resilience'].sum())
        policy_count = len(group)
        summary_rows.append({
            'country_iso': iso,
            'country': country_name,
            'resilience_score': resilience_score,
            'policy_count': policy_count
        })
        
    df_summary = pd.DataFrame(summary_rows)
    # Sort by resilience_score descending, then country name
    df_summary = df_summary.sort_values(by=['resilience_score', 'country'], ascending=[False, True])
    df_summary.to_csv("c:/Users/laure/Documents/DSPP_local/country_resilience_scores.csv", index=False)
    print("Exported country_resilience_scores.csv.")
    
    print("\nQuality Checks:")
    # Print top 5 terms/categories that generated the most matches
    sorted_terms = sorted(term_match_counts.items(), key=lambda x: x[1], reverse=True)
    print("Top 5 terms/categories by matches:")
    for term, count in sorted_terms[:5]:
        print(f"  - {term}: {count} matches")
        
    print("\nTop 10 Countries by resilience_score:")
    print(df_summary.head(10).to_string(index=False))

if __name__ == '__main__':
    main()
