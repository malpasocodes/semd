# utils/data_utils.py
import pandas as pd
import streamlit as st

@st.cache_data
def load_mobility_data():
    """
    Load mobility dataset (four-year and two-year colleges only)
    Returns filtered dataframe excluding less than two-year institutions
    """
    try:
        df = pd.read_csv("data/mrc_table2.csv")
        
        # Filter for only four-year colleges
        df = df[df['iclevel'] == 1]
        
        return df
        
    except Exception as e:
        st.error(f"Error loading mobility data: {e}")
        return None


@st.cache_data
def load_cost_data():
    """
    Load cost dataset with tuition information
    """
    try:
        df = pd.read_csv("data/mrc_table10.csv")

        # Filter for only four-year colleges
        df = df[df['iclevel'] == 1]
        return df
    except Exception as e:
        st.error(f"Error loading cost data: {e}")
        return None

def merge_datasets():
    """
    Merge mobility and cost datasets
    """
    df_mobility = load_mobility_data()
    df_cost = load_cost_data()
    
    if df_mobility is None or df_cost is None:
        return None
    
    try:
        merged_df = pd.merge(
            df_mobility,
            df_cost[['super_opeid', 'sticker_price_2013', 'scorecard_netprice_2013']],
            on='super_opeid',
            how='inner'
        )
        return merged_df
    except Exception as e:
        st.error(f"Error merging datasets: {e}")
        return None

def check_mobility_columns(df):
    """
    Check if all required mobility columns exist in the dataset
    """
    # Expected column patterns
    parent_quintiles = [f'par_q{i}' for i in range(1, 6)]
    conditional_patterns = [
        f'kq{k}_cond_parq{p}' 
        for p in range(1, 6)  # parent quintiles
        for k in range(1, 6)  # kid quintiles
    ]
    
    # Check columns
    missing_columns = []
    existing_columns = []
    
    # Check parent quintile columns
    for col in parent_quintiles:
        if col in df.columns:
            existing_columns.append(col)
        else:
            missing_columns.append(col)
    
    # Check conditional probability columns
    for col in conditional_patterns:
        if col in df.columns:
            existing_columns.append(col)
        else:
            missing_columns.append(col)
    
    # Display summary using Streamlit
    st.write("\nColumn Verification Summary:")
    st.write(f"Total expected columns: {len(parent_quintiles) + len(conditional_patterns)}")
    st.write(f"Found columns: {len(existing_columns)}")
    st.write(f"Missing columns: {len(missing_columns)}")
    
    if missing_columns:
        st.write("\nMissing columns:")
        for col in missing_columns:
            st.write(f"- {col}")
            
    # Show sample of existing columns
    st.write("\nSample of existing columns:")
    st.write(sorted(existing_columns)[:10])
    
    return {
        'has_all_columns': len(missing_columns) == 0,
        'existing_columns': existing_columns,
        'missing_columns': missing_columns
    }
