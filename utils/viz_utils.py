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
            
        # Calculate probabilities using new generic column names
        q5_prob = tier_df['kq5_cond_parq'].mean()
        q4_prob = tier_df['kq4_cond_parq'].mean()
        q3_prob = tier_df['kq3_cond_parq'].mean()
        q2_prob = tier_df['kq2_cond_parq'].mean()
        q1_prob = tier_df['kq1_cond_parq'].mean()
        
        # Calculate Q4+Q5 probability
        q4q5_prob = (q5_prob + q4_prob) * 100
        
        # Calculate average bottom quintile enrollment if column exists
        avg_q1_pct = tier_df['par_q'].mean() * 100 if 'par_q' in tier_df.columns else 0
        
        # Create cumulative probabilities for line plot
        x = ['Q5', 'Q4', 'Q3', 'Q2', 'Q1']
        y_cumulative = [
            q5_prob * 100,
            q4q5_prob,  # This is the Q4+Q5 point
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
        hover_text = [
            "Tier: " + tier_name,
            "Quintile: %{x}",
            "Cumulative Probability: %{y:.1f}%",
            "Colleges: " + str(len(tier_df))
        ]
        if avg_q1_pct > 0:
            hover_text.append(f"Avg Q1 Students: {avg_q1_pct:.1f}%")
        hover_text.append("<extra></extra>")
        
        fig_line.add_trace(go.Scatter(
            x=x, y=y_cumulative,
            mode='lines+markers',
            name=f"{tier_name} (n={len(tier_df)})",
            line=dict(color=color, width=2),
            marker=dict(size=8),
            hovertemplate="<br>".join(hover_text)
        ))
        
        # Add annotation for Q4+Q5 with different placement for each tier
        if tier_name == tier1:
            # First tier annotation (left side, pointing down-right)
            fig_line.add_annotation(
                x='Q4',
                y=q4q5_prob,
                text=f"Q4+Q5 = {q4q5_prob:.1f}%",
                showarrow=True,
                arrowhead=1,
                ax=-60,  # Move box to the left
                ay=-60,  # Move box down
                font=dict(color=color),
                bordercolor=color,
                borderwidth=2,
                borderpad=4,
                bgcolor="white",
                opacity=0.8
            )
        else:
            # Second tier annotation (right side, as before but longer arrow)
            fig_line.add_annotation(
                x='Q4',
                y=q4q5_prob,
                text=f"Q4+Q5 = {q4q5_prob:.1f}%",
                showarrow=True,
                arrowhead=1,
                ax=60,   # Longer arrow to the right
                ay=-60,  # Longer arrow up
                font=dict(color=color),
                bordercolor=color,
                borderwidth=2,
                borderpad=4,
                bgcolor="white",
                opacity=0.8
            )
        
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
        xaxis_categoryarray=['Q5', 'Q4', 'Q3', 'Q2', 'Q1'],
        showlegend=True
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

def plot_mobility_ladder_cdf(df):
    """
    Creates a comparative cumulative probability plot showing mobility patterns
    across different college tiers
    
    Parameters:
    -----------
    df : pd.DataFrame
        Processed mobility ladder DataFrame from create_mobility_ladder()
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
        9: "Two-year (public and private)",
        10: "Four-year for-profit",
        11: "Two-year for-profit",
        12: "Less than two year schools"
    }
    
    # Create two selectboxes side by side for tier selection
    col1, col2 = st.sidebar.columns(2)
    with col1:
        selected_tier1 = st.selectbox(
            "Select First Tier",
            options=list(tier_map.values()),
            key='tier1'
        )
    
    with col2:
        remaining_tiers = [t for t in tier_map.values() if t != selected_tier1]
        selected_tier2 = st.selectbox(
            "Select Second Tier",
            options=remaining_tiers,
            key='tier2'
        )
    
    # Create plotly figure
    fig = go.Figure()
    
    # Display number of colleges meeting criteria
    st.sidebar.markdown(f"### Colleges Meeting Criteria")
    
    # Store college lists for display later
    college_data = {}
    
    # Process both selected tiers
    for tier_name, color in [(selected_tier1, '#1a9850'), (selected_tier2, '#d73027')]:
        # Get tier ID
        tier_id = [k for k, v in tier_map.items() if v == tier_name][0]
        
        # Filter data for this tier
        tier_df = df[df['tier'] == tier_id].copy()
        
        # Store college data for this tier
        college_data[tier_name] = tier_df.copy()
        
        # Show number of colleges in sidebar
        st.sidebar.markdown(f"**{tier_name}**: {len(tier_df)} colleges")
        
        if len(tier_df) == 0:
            st.warning(f"No colleges in {tier_name} meet the criteria.")
            continue
        
        # Calculate mean probabilities using correct column names
        q5_prob = tier_df['kq5_cond_parq'].mean()
        q4_prob = tier_df['kq4_cond_parq'].mean()
        q3_prob = tier_df['kq3_cond_parq'].mean()
        q2_prob = tier_df['kq2_cond_parq'].mean()
        q1_prob = tier_df['kq1_cond_parq'].mean()
        
        # Create cumulative probabilities
        x = ['Q5', 'Q4', 'Q3', 'Q2', 'Q1']
        y = [
            q5_prob * 100,
            (q5_prob + q4_prob) * 100,
            (q5_prob + q4_prob + q3_prob) * 100,
            (q5_prob + q4_prob + q3_prob + q2_prob) * 100,
            100  # Total should be 100%
        ]
        
        fig.add_trace(go.Scatter(
            x=x, y=y, mode='lines+markers', name=f"{tier_name} (n={len(tier_df)})",
            line=dict(color=color, width=2), marker=dict(size=8),
            hovertemplate="<br>".join([
                "Tier: " + tier_name,
                "Quintile: %{x}",
                "Cumulative Probability: %{y:.1f}%",
                "Colleges: " + str(len(tier_df)),
                "<extra></extra>"
            ])
        ))
    
    # Update layout
    fig.update_layout(
        title="Mobility Ladder Comparison",
        xaxis_title="Income Quintile",
        yaxis_title="Cumulative Probability (%)",
        yaxis_range=[0, 100],
        xaxis_categoryorder='array',
        xaxis_categoryarray=['Q5', 'Q4', 'Q3', 'Q2', 'Q1'],
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Display plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Add comparative interpretation
    st.markdown("### Comparative Analysis")
    
    col1, col2 = st.columns(2)
    
    # Process and display stats for each tier
    for tier_name, col in [(selected_tier1, col1), (selected_tier2, col2)]:
        tier_df = college_data[tier_name]
        
        if len(tier_df) > 0:
            q5_prob = tier_df['kq5_cond_parq'].mean()
            q4_prob = tier_df['kq4_cond_parq'].mean()
            q3_prob = tier_df['kq3_cond_parq'].mean()
            q2_prob = tier_df['kq2_cond_parq'].mean()
            q1_prob = tier_df['kq1_cond_parq'].mean()
            
            with col:
                st.markdown(f"""
                **{tier_name}** (n={len(tier_df)})
                
                Cumulative Probabilities:
                - Q5: {q5_prob * 100:.1f}%
                - Q4+: {(q5_prob + q4_prob) * 100:.1f}%
                - Q3+: {(q5_prob + q4_prob + q3_prob) * 100:.1f}%
                - Q2+: {(q5_prob + q4_prob + q3_prob + q2_prob) * 100:.1f}%
                - Total: 100%
                """)

def plot_mobility_sankey(df, tier_name):
    """
    Create a Sankey diagram showing student flows between quintiles
    """
    # Calculate flows
    source = []  # Bottom quintile (repeated)
    target = []  # Destination quintiles
    value = []   # Percentage of students
    
    quintile_names = ['Bottom Quintile', 'Q2', 'Q3', 'Q4', 'Top Quintile']
    
    flows = [
        df['kq1_cond_parq'].mean(),
        df['kq2_cond_parq'].mean(),
        df['kq3_cond_parq'].mean(),
        df['kq4_cond_parq'].mean(),
        df['kq5_cond_parq'].mean()
    ]
    
    for i, flow in enumerate(flows):
        source.append(0)  # Always from bottom quintile
        target.append(i+1)
        value.append(flow * 100)
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 0.5),
            label = quintile_names,
            color = "blue"
        ),
        link = dict(
            source = source,
            target = target,
            value = value,
            color = 'rgba(0,0,100,0.2)'
        )
    )])
    
    fig.update_layout(
        title=f"Student Mobility Flows - {tier_name}",
        font_size=12,
        height=400
    )
    
    return fig

def plot_mobility_alluvial(df, tier_name):
    """
    Create an alluvial plot showing transitions between quintiles
    """
    import plotly.graph_objects as go
    
    # Calculate probabilities for each quintile
    probs = [
        df['kq5_cond_parq'].mean(),
        df['kq4_cond_parq'].mean(),
        df['kq3_cond_parq'].mean(),
        df['kq2_cond_parq'].mean(),
        df['kq1_cond_parq'].mean()
    ]
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each flow
    y_positions = [5, 4, 3, 2, 1]
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
    
    for i, (prob, y_pos, color) in enumerate(zip(probs, y_positions, colors)):
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[1, y_pos],
            mode='lines',
            line=dict(width=prob*100, color=color),
            name=f'To Q{5-i}',
            hovertemplate=f"Probability: {prob*100:.1f}%"
        ))
    
    fig.update_layout(
        title=f"Mobility Transitions - {tier_name}",
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            title="Origin → Destination"
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            title="Income Quintile"
        ),
        showlegend=True,
        height=400
    )
    
    return fig

def plot_mobility_area(df, tier_name):
    """
    Create a stacked area chart showing cumulative probabilities
    """
    # Calculate cumulative probabilities
    probs = [
        df['kq5_cond_parq'].mean() * 100,
        df['kq4_cond_parq'].mean() * 100,
        df['kq3_cond_parq'].mean() * 100,
        df['kq2_cond_parq'].mean() * 100,
        df['kq1_cond_parq'].mean() * 100
    ]
    
    fig = go.Figure()
    
    quintiles = ['Q5', 'Q4', 'Q3', 'Q2', 'Q1']
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
    
    for i, (quintile, prob, color) in enumerate(zip(quintiles, probs, colors)):
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[0, prob],
            fill='tonexty',
            name=quintile,
            line=dict(color=color),
            hovertemplate=f"{quintile}: {prob:.1f}%"
        ))
    
    fig.update_layout(
        title=f"Mobility Distribution - {tier_name}",
        xaxis_title="Origin (Bottom Quintile) → Destination",
        yaxis_title="Probability (%)",
        yaxis_range=[0, 100],
        showlegend=True,
        height=400
    )
    
    return fig