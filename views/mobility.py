# views/level1a_mobility_ladder.py
import streamlit as st
from utils.mobility_utils import create_mobility_ladder
from utils.viz_utils import plot_mobility_sankey, plot_mobility_alluvial, plot_mobility_area

def show_mobility_visualizations(df):
    """
    Show detailed visualizations of mobility patterns
    """
    st.title("Detailed Mobility Visualizations")
    st.markdown("""
    This page provides additional visualizations to help understand mobility patterns
    across different college tiers.
    """)
    
    # Create mobility ladder DataFrame
    df_mobility = create_mobility_ladder(df)
    
    # Create tier selection
    tier_map = {
        1: "Ivy Plus",
        2: "Other elite schools",
        3: "Highly selective public",
        4: "Highly selective private",
        5: "Selective public",
        6: "Selective private",
        7: "Nonselective 4-year public",
        8: "Nonselective 4-year private",
        10: "Four-year for-profit"
    }
    
    selected_tier = st.selectbox(
        "Select College Tier",
        ["All"] + list(tier_map.values())
    )
    
    if selected_tier == "All":
        tier_df = df_mobility
    else:
        tier_id = next(k for k, v in tier_map.items() if v == selected_tier)
        tier_df = df_mobility[df_mobility['tier'] == tier_id]
    
    # Display Sankey diagram
    st.subheader("Student Flow Visualization")
    st.markdown("""
    This Sankey diagram shows how students from the bottom quintile flow to different income quintiles.
    The width of each flow represents the percentage of students.
    """)
    sankey_fig = plot_mobility_sankey(tier_df, selected_tier)
    st.plotly_chart(sankey_fig, use_container_width=True)
    
    # Display Alluvial plot
    st.subheader("Mobility Transitions")
    st.markdown("""
    This visualization shows the transitions from bottom quintile to each destination quintile.
    The thickness of each line represents the percentage of students making that transition.
    """)
    alluvial_fig = plot_mobility_alluvial(tier_df, selected_tier)
    st.plotly_chart(alluvial_fig, use_container_width=True)
    
    # Display Area chart
    st.subheader("Cumulative Mobility Distribution")
    st.markdown("""
    This stacked area chart shows the cumulative distribution of students across quintiles.
    Each color represents a different destination quintile.
    """)
    area_fig = plot_mobility_area(tier_df, selected_tier)
    st.plotly_chart(area_fig, use_container_width=True)