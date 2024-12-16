import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def show_enrollment_patterns(df):
    """
    Show enrollment patterns for selected college type
    """
    st.title("Enrollment Explorer")
    
    # Create tier selection
    tier_map = {
        "Ivy Plus": 1,
        "Other Elite": 2,
        "Highly Selective Public": 3,
        "Highly Selective Private": 4,
        "Selective Public": 5,
        "Selective Private": 6,
        "Nonselective 4-year Public": 7,
        "Nonselective 4-year Private": 8,
        "Four-year For-profit": 10
    }
    
    selected_tier = st.sidebar.selectbox(
        "Select College Type",
        options=list(tier_map.keys())
    )
    
    # Filter data for selected tier
    tier_id = tier_map[selected_tier]
    tier_df = df[df['tier'] == tier_id]
    
    # Calculate mean enrollment percentages
    quintile_cols = [f'par_q{i}' for i in range(1, 6)]
    top_cols = ['par_top1pc', 'par_toppt1pc']
    
    mean_enrollments = {
        'quintiles': [tier_df[col].mean() * 100 for col in quintile_cols],
        'top_pcts': [tier_df[col].mean() * 100 for col in top_cols]
    }
    
    # Calculate cumulative percentages for quintiles only
    cumulative_values = [
        mean_enrollments['quintiles'][0],  # Q1
        sum(mean_enrollments['quintiles'][:2]),  # Q1+Q2
        sum(mean_enrollments['quintiles'][:3]),  # Q1+Q2+Q3
        sum(mean_enrollments['quintiles'][:4]),  # Q1+Q2+Q3+Q4
        sum(mean_enrollments['quintiles'][:5])   # Q1+Q2+Q3+Q4+Q5
    ]
    
    # Create bar chart
    fig = go.Figure()
    
    # Create x-axis labels including both top percentiles
    x_labels = [f'Q{i}' for i in range(1, 6)] + ['Top 1%', 'Top 0.1%']
    
    # Create y-values including both top percentiles
    y_values = mean_enrollments['quintiles'] + mean_enrollments['top_pcts']
    
    # Add bars first (lower layer)
    fig.add_trace(go.Bar(
        x=x_labels,
        y=y_values,
        text=[f'{val:.1f}%' for val in y_values],
        textposition='auto',
        marker_color='#1f77b4',
        width=0.3,
        name='Enrollment'
    ))
    
    # Add cumulative line with offset to appear above bars
    offset = 5  # Increased base offset
    
    # Create custom offsets for each point
    custom_offsets = [
        offset + 5,  # Increased space for Q1 (first point)
        offset,      # Regular offset for Q2
        offset,      # Regular offset for Q3
        offset,      # Regular offset for Q4
        offset - 3   # Negative offset for Q5 (last point)
    ]
    
    fig.add_trace(go.Scatter(
        x=x_labels[:5],  # Only quintiles, not top percentiles
        y=[val + offset for val, offset in zip(cumulative_values, custom_offsets)],
        mode='lines+markers+text',
        text=[f'{val:.1f}%' for val in cumulative_values],
        textposition=['top center', 'top center', 'top center', 'top center', 'bottom right'],  # Changed last label to bottom
        line=dict(color='#e74c3c', width=2),
        marker=dict(size=8),
        name='Cumulative',
        hovertemplate="Cumulative: %{text}<extra></extra>"
    ))
    
    # Update layout with increased y-range
    fig.update_layout(
        title=f"Parent Income Distribution - {selected_tier}",
        xaxis_title="Parent Income Group",
        yaxis_title="Percentage of Students",
        yaxis_range=[0, max(max(y_values), max(cumulative_values) + max(custom_offsets) + 2)],  # Adjusted range
        showlegend=True,
        height=400,
        bargap=0.2,
        width=800,
        margin=dict(l=50, r=50, t=50, b=50),  # Added top and bottom margins
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display summary statistics
    st.markdown("### Summary Statistics")
    st.markdown(f"Number of institutions: {len(tier_df)}")
    
    # Display distribution metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Quintile Distribution")
        for i, pct in enumerate(mean_enrollments['quintiles'], 1):
            st.markdown(f"Q{i}: {pct:.1f}%")
    
    with col2:
        st.markdown("#### Top Percentile Distribution")
        st.markdown(f"Top 1%: {mean_enrollments['top_pcts'][0]:.1f}%")
        st.markdown(f"Top 0.1%: {mean_enrollments['top_pcts'][1]:.1f}%") 