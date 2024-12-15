import streamlit as st
import pandas as pd
from utils.mobility_utils import create_mobility_ladder
from utils.viz_utils import plot_mobility_ladder, plot_mobility_sankey, plot_mobility_alluvial, plot_mobility_area

def show_mobility_ladder(df=None, view_type="cumulative", parent_quintile=1):
    """
    Show mobility ladder analysis
    
    Parameters:
    -----------
    df : pd.DataFrame, optional
        Pre-filtered DataFrame. If None, loads and filters the data internally
    view_type : str
        Type of visualization to show: "cumulative", "individual", or "transitions"
    parent_quintile : int
        Parent income quintile to analyze (1-5)
    """
    # Set title based on view type
    titles = {
        "cumulative": f"Cumulative Probability Analysis (Parent Q{parent_quintile})",
        "individual": f"Individual Probability Analysis (Parent Q{parent_quintile})",
        "transitions": f"Mobility Transitions Analysis (Parent Q{parent_quintile})"
    }
    
    st.title(f"Economic Mobility: {titles[view_type]}")
    st.markdown(f"""
    This analysis shows where students from the {parent_quintile}{'st' if parent_quintile == 1 else 'nd' if parent_quintile == 2 else 'rd' if parent_quintile == 3 else 'th'} income quintile end up 
    for each college. The percentages show the proportion of students moving 
    to each income quintile.
    """)
    
    # Load data if not provided
    if df is None:
        df = pd.read_csv("data/mrc_table2.csv")
        df = df[df['iclevel'] == 1]  # Filter for 4-year colleges
    
    # Create mobility ladder DataFrame
    df_mobility = create_mobility_ladder(df, parent_quintile=parent_quintile)
    
    # Create tier selection in sidebar
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
    
    # Allow selection of types to compare
    st.sidebar.markdown("### Compare College Types")
    tier1 = st.sidebar.selectbox(
        "First Type",
        ["All"] + list(tier_map.values()),
        key="tier1_select"
    )
    
    remaining_tiers = ["All"] + [t for t in tier_map.values() if t != tier1]
    tier2 = st.sidebar.selectbox(
        "Second Type",
        remaining_tiers,
        key="tier2_select"
    )
    
    # Create and display appropriate visualization
    fig_line, fig_bar, college_data = plot_mobility_ladder(df_mobility, tier1, tier2)
    
    if view_type == "cumulative":
        st.plotly_chart(fig_line, use_container_width=True)
    elif view_type == "individual":
        st.plotly_chart(fig_bar, use_container_width=True)
    else:  # transitions
        st.plotly_chart(fig_line, use_container_width=True)  # You might want to create a new visualization for transitions
    
    # Display college counts and statistics
    st.markdown("### College Statistics")
    
    col1, col2 = st.columns(2)
    
    for tier_name, col in [(tier1, col1), (tier2, col2)]:
        if tier_name in college_data:
            tier_df = college_data[tier_name]
            with col:
                st.markdown(f"""
                #### {tier_name}
                - Number of colleges: {len(tier_df)}
                - Average Q{parent_quintile} enrollment: {(tier_df['par_q'].mean() * 100):.1f}%
                - Average Q5 mobility rate: {(tier_df['kq5_cond_parq'].mean() * 100):.1f}%
                """)
    
    # Display colleges for each type
    st.markdown("### Colleges by Type")
    
    col1, col2 = st.columns(2)
    
    column_config = {
        'name': 'College Name',
        'par_q': f'Q{parent_quintile} Enrollment %',
        'mobility_rate': 'Q4+Q5 Mobility Rate'
    }
    
    for tier_name, col in [(tier1, col1), (tier2, col2)]:
        if tier_name in college_data:
            tier_df = college_data[tier_name]
            with col:
                st.markdown(f"#### {tier_name} Colleges")
                # Calculate Q4+Q5 mobility rate
                tier_df['mobility_rate'] = tier_df['kq4_cond_parq'] + tier_df['kq5_cond_parq']
                
                # Create display DataFrame with selected columns
                display_df = tier_df[['name', 'par_q', 'mobility_rate']].copy()
                
                # Format percentages
                display_df['par_q'] = (display_df['par_q'] * 100).round(1)
                display_df['mobility_rate'] = (display_df['mobility_rate'] * 100).round(1)
                
                st.dataframe(
                    display_df,
                    column_config=column_config,
                    height=400
                )

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

def show_data_verification(df, parent_quintile):
    """
    Show detailed data verification for mobility analysis
    """
    st.title(f"Data Verification - Parent Q{parent_quintile}")
    
    # Create processed dataset
    df_mobility = create_mobility_ladder(df, parent_quintile=parent_quintile)
    
    # 1. Show summary statistics
    st.header("Summary Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Raw Data")
        raw_stats = pd.DataFrame({
            'Metric': [
                f'par_q{parent_quintile}',
                f'kq1_cond_parq{parent_quintile}',
                f'kq2_cond_parq{parent_quintile}',
                f'kq3_cond_parq{parent_quintile}',
                f'kq4_cond_parq{parent_quintile}',
                f'kq5_cond_parq{parent_quintile}'
            ],
            'Mean': [
                df[f'par_q{parent_quintile}'].mean() * 100,
                df[f'kq1_cond_parq{parent_quintile}'].mean() * 100,
                df[f'kq2_cond_parq{parent_quintile}'].mean() * 100,
                df[f'kq3_cond_parq{parent_quintile}'].mean() * 100,
                df[f'kq4_cond_parq{parent_quintile}'].mean() * 100,
                df[f'kq5_cond_parq{parent_quintile}'].mean() * 100
            ]
        })
        st.dataframe(raw_stats.style.format({'Mean': '{:.1f}%'}))
        
        # Check sum of probabilities
        prob_sum = sum([
            df[f'kq{i}_cond_parq{parent_quintile}'].mean() for i in range(1, 6)
        ]) * 100
        st.metric("Sum of Probabilities", f"{prob_sum:.1f}%")
    
    with col2:
        st.subheader("Processed Data")
        processed_stats = pd.DataFrame({
            'Metric': ['par_q'] + [f'kq{i}_cond_parq' for i in range(1, 6)],
            'Mean': [
                df_mobility['par_q'].mean() * 100,
                df_mobility['kq1_cond_parq'].mean() * 100,
                df_mobility['kq2_cond_parq'].mean() * 100,
                df_mobility['kq3_cond_parq'].mean() * 100,
                df_mobility['kq4_cond_parq'].mean() * 100,
                df_mobility['kq5_cond_parq'].mean() * 100
            ]
        })
        st.dataframe(processed_stats.style.format({'Mean': '{:.1f}%'}))
    
    # 2. Show sample comparisons
    st.header("Sample Data Comparison")
    sample_size = st.slider("Number of colleges to show", 5, 20, 10)
    
    sample_df = pd.merge(
        df[[
            'name', 
            f'par_q{parent_quintile}',
            f'kq1_cond_parq{parent_quintile}',
            f'kq5_cond_parq{parent_quintile}'
        ]].head(sample_size),
        df_mobility[['name', 'par_q', 'kq1_cond_parq', 'kq5_cond_parq']].head(sample_size),
        on='name',
        suffixes=('_raw', '_processed')
    )
    
    st.dataframe(
        sample_df.style.format({
            f'par_q{parent_quintile}': '{:.1%}',
            'par_q': '{:.1%}',
            f'kq1_cond_parq{parent_quintile}': '{:.1%}',
            'kq1_cond_parq': '{:.1%}',
            f'kq5_cond_parq{parent_quintile}': '{:.1%}',
            'kq5_cond_parq': '{:.1%}'
        })
    )
    
    # 3. Distribution plots
    st.header("Value Distributions")
    
    # Create distribution plot using plotly express
    import plotly.express as px
    
    # Create a long-format DataFrame for the distributions
    dist_df = pd.DataFrame({
        f'Q{parent_quintile} Enrollment': df_mobility['par_q'] * 100,
        'Stay in Q1 Rate': df_mobility['kq1_cond_parq'] * 100,
        'Rise to Q5 Rate': df_mobility['kq5_cond_parq'] * 100
    })
    
    # Melt the DataFrame for plotting
    dist_df_long = dist_df.melt(var_name='Metric', value_name='Percentage')
    
    # Create box plot
    fig = px.box(
        dist_df_long,
        x='Metric',
        y='Percentage',
        title=f"Distribution of Key Metrics (Parent Q{parent_quintile})",
        points="all"  # Show all points
    )
    
    fig.update_layout(
        yaxis_title="Percentage",
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)