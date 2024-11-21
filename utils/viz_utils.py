
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import numpy as np
import pandas as pd

def plot_mobility_ladder(df, tier1, tier2):
    """
    Create mobility ladder plot and bar chart comparing two tiers
    Returns both figures for display
    """
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
    
    # Create line plot
    fig_line = go.Figure()
    # Create bar plot
    fig_bar = go.Figure()
    college_data = {}
    
    # Process both tiers
    for tier_name, color in [(tier1, '#1a9850'), (tier2, '#1f77b4')]:
        if tier_name == "All":
            tier_df = df.copy()
            college_data[tier_name] = tier_df
        else:
            try:
                tier_id = next(k for k, v in tier_map.items() if v == tier_name)
                tier_df = df[df['tier'] == tier_id].copy()
                college_data[tier_name] = tier_df
            except StopIteration:
                continue
            
        if len(tier_df) == 0:
            continue
            
        # Calculate probabilities
        q5_prob = tier_df['kq5_cond_parq1'].mean()
        q4_prob = tier_df['kq4_cond_parq1'].mean()
        q3_prob = tier_df['kq3_cond_parq1'].mean()
        q2_prob = tier_df['kq2_cond_parq1'].mean()
        q1_prob = tier_df['kq1_cond_parq1'].mean()
        avg_q1_pct = tier_df['par_q1'].mean() * 100
        
        # Create cumulative probabilities for line plot
        x = ['Q5', 'Q4', 'Q3', 'Q2', 'Q1']
        y_cumulative = [
            q5_prob * 100,
            (q5_prob + q4_prob) * 100,
            (q5_prob + q4_prob + q3_prob) * 100,
            (q5_prob + q4_prob + q3_prob + q2_prob) * 100,
            100
        ]
        
        # Individual probabilities for bar plot
        y_individual = [
            q5_prob * 100,
            q4_prob * 100,
            q3_prob * 100,
            q2_prob * 100,
            q1_prob * 100
        ]
        
        # Add line plot trace
        fig_line.add_trace(go.Scatter(
            x=x, y=y_cumulative,
            mode='lines+markers',
            name=f"{tier_name} (n={len(tier_df)})",
            line=dict(color=color, width=2),
            marker=dict(size=8),
            hovertemplate="<br>".join([
                "Tier: " + tier_name,
                "Quintile: %{x}",
                "Cumulative Probability: %{y:.1f}%",
                "Colleges: " + str(len(tier_df)),
                f"Avg Q1 Students: {avg_q1_pct:.1f}%",
                "<extra></extra>"
            ])
        ))
        
        # Add bar plot trace
        fig_bar.add_trace(go.Bar(
            x=x,
            y=y_individual,
            name=f"{tier_name} (n={len(tier_df)})",
            marker_color=color,
            hovertemplate="<br>".join([
                "Tier: " + tier_name,
                "Quintile: %{x}",
                "Probability: %{y:.1f}%",
                "<extra></extra>"
            ])
        ))
    
    # Update line plot layout
    fig_line.update_layout(
        title="Mobility Ladder - Cumulative Probabilities",
        xaxis_title="Income Quintile",
        yaxis_title="Cumulative Probability (%)",
        yaxis_range=[0, 100],
        xaxis_categoryorder='array',
        xaxis_categoryarray=['Q5', 'Q4', 'Q3', 'Q2', 'Q1']
    )
    
    # Update bar plot layout
    fig_bar.update_layout(
        title="Mobility Ladder - Individual Probabilities",
        xaxis_title="Income Quintile",
        yaxis_title="Probability (%)",
        yaxis_range=[0, 100],
        xaxis_categoryorder='array',
        xaxis_categoryarray=['Q5', 'Q4', 'Q3', 'Q2', 'Q1'],
        barmode='group'
    )
    
    return fig_line, fig_bar, college_data

def plot_cost_mobility(df):
    """
    Create scatter plot of cost vs mobility
    """
    fig = px.scatter(
        df,
        x='sticker_price_2013',
        y='mobility_q4q5',
        color='tier_name',
        title="Mobility Rate vs. Cost of Attendance",
        labels={
            'sticker_price_2013': "Cost of Attendance ($)",
            'mobility_q4q5': "Mobility Rate",
            'tier_name': "Institution Type"
        }
    )
    
    fig.update_layout(
        xaxis_tickformat="$,.0f",
        yaxis_tickformat=".0%",
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        height=600,
        xaxis=dict(autorange="reversed")
    )
    
    return fig

def display_stats(df, price_col='sticker_price_2013'):
    """
    Display summary statistics
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Number of Colleges", len(df))
    with col2:
        st.metric("Mean Cost", f"${df[price_col].mean():,.0f}")
    with col3:
        correlation = df[price_col].corr(df['mobility_q4q5'])
        st.metric("Cost-Mobility Correlation", f"{correlation:.3f}")