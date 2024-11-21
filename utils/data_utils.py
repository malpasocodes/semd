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
