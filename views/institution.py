import streamlit as st
import pandas as pd

def show_institution_profile(df):
    """
    Show detailed profile for a single institution
    """
    st.title("Institution Explorer")
    
    # Move institution selection to sidebar with filters
    st.sidebar.markdown("### Institution Selection")
    
    # 1. Institution Tier filter (now first)
    tier_map = {
        "All": None,
        "Ivy Plus": 1,
        "Other Elite": 2,
        "Highly Selective Public": 3,
        "Highly Selective Private": 4,
        "Selective Public": 5,
        "Selective Private": 6,
        "Nonselective 4-year Public": 7,
        "Nonselective 4-year Private": 8,
        "Two-year (Public and Private)": 9,
        "Four-year For-profit": 10,
        "Two-year For-profit": 11,
        "Less than Two Year": 12
    }
    selected_tier = st.sidebar.selectbox(
        "Institution Tier",
        options=list(tier_map.keys())
    )
    
    # 2. State filter
    states = ["All"] + sorted(df['state'].unique().tolist())
    selected_state = st.sidebar.selectbox(
        "State",
        options=states
    )
    
    # Apply filters to institution list
    filtered_df = df.copy()
    if selected_state != "All":
        filtered_df = filtered_df[filtered_df['state'] == selected_state]
    if selected_tier != "All":
        filtered_df = filtered_df[filtered_df['tier'] == tier_map[selected_tier]]
    
    # Create searchable dropdown with filtered institutions
    institutions = sorted(filtered_df['name'].unique())
    
    if len(institutions) == 0:
        st.error("No institutions match the selected filters. Please adjust your selection.")
        return
    
    selected_institution = st.sidebar.selectbox(
        "Select Institution",
        institutions,
        help="Type to search for an institution"
    )
    
    # Get data for selected institution
    inst_data = df[df['name'] == selected_institution].iloc[0]
    
    # Display institution name prominently
    st.markdown(f"## {selected_institution}")
    
    # Add a divider
    st.markdown("---")
    
    # Create three columns for key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Institution Type")
        st.markdown(f"**{inst_data['type']}**")
    
    with col2:
        st.markdown("#### Location")
        st.markdown(f"**{inst_data.get('state', 'N/A')}**")
    
    with col3:
        st.markdown("#### Tier")
        try:
            tier_name = next(name for name, id in tier_map.items() if id == inst_data['tier'])
            st.markdown(f"**{tier_name}**")
        except (StopIteration, KeyError):
            st.markdown("**Other**")
    
    # Add cost information in a separate section
    st.markdown("### Cost Information (2013)")
    
    # Single column for published price
    st.metric(
        "Published Price",
        f"${inst_data['sticker_price_2013']:,.0f}",
        help="Total published cost before financial aid (tuition, fees, room & board)"
    )
    
    # Display mobility metrics
    st.markdown("### Mobility Metrics")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Parent Income Distribution", "Mobility Rates"])
    
    with tab1:
        # Show only the bar chart
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # Create x-axis labels including both top percentiles
        x_labels = [f'Q{i}' for i in range(1, 6)] + ['Top 1%', 'Top 0.1%']
        
        # Create y-values including both top percentiles
        y_values = [inst_data[f'par_q{i}'] * 100 for i in range(1, 6)] + \
                  [inst_data['par_top1pc'] * 100, inst_data['par_toppt1pc'] * 100]
        
        # Add bars with reduced width and spacing
        fig.add_trace(go.Bar(
            x=x_labels,
            y=y_values,
            text=[f'{val:.1f}%' for val in y_values],
            textposition='auto',
            marker_color='#1f77b4',
            width=0.3,  # Reduced from 0.5 to 0.3
        ))
        
        # Update layout with tighter bar spacing and reduced width
        fig.update_layout(
            title="Parent Income Distribution",
            xaxis_title="Parent Income Group",
            yaxis_title="Percentage of Students",
            yaxis_range=[0, max(y_values) * 1.2],
            showlegend=False,
            height=400,
            bargap=0.2,  # Control spacing between bars
            width=800,   # Control overall chart width
            margin=dict(l=50, r=50)  # Add margins to ensure labels are visible
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Create grouped bar chart for mobility rates
        import plotly.graph_objects as go
        
        # Prepare data
        parent_quintiles = [f'Q{i}' for i in range(1, 6)]
        q4_rates = [inst_data[f'kq4_cond_parq{i}'] * 100 for i in range(1, 6)]
        q5_rates = [inst_data[f'kq5_cond_parq{i}'] * 100 for i in range(1, 6)]
        q4q5_rates = [(q4 + q5) for q4, q5 in zip(q4_rates, q5_rates)]
        
        # Create figure
        fig = go.Figure()
        
        # Add bars for each rate type with reduced width
        fig.add_trace(go.Bar(
            name='Q5 Rate',
            x=parent_quintiles,
            y=q5_rates,
            text=[f'{val:.1f}%' for val in q5_rates],
            textposition='auto',
            marker_color='#2ecc71',
            width=0.2
        ))
        
        fig.add_trace(go.Bar(
            name='Q4 Rate',
            x=parent_quintiles,
            y=q4_rates,
            text=[f'{val:.1f}%' for val in q4_rates],
            textposition='auto',
            marker_color='#3498db',
            width=0.2
        ))
        
        # Add line for combined Q4+Q5 rate
        fig.add_trace(go.Scatter(
            name='Q4+Q5 Rate',
            x=parent_quintiles,
            y=q4q5_rates,
            mode='lines+markers+text',
            text=[f'{val:.1f}%' for val in q4q5_rates],
            textposition='top center',
            line=dict(color='#e74c3c', width=2),
            marker=dict(size=8)
        ))
        
        # Update layout
        fig.update_layout(
            title="Mobility Rates by Parent Income",
            xaxis_title="Parent Income Quintile",
            yaxis_title="Rate (%)",
            barmode='group',
            yaxis_range=[0, max(q4q5_rates) * 1.2],
            height=500,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99
            )
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.markdown("""
        **Explanation:**
        - Bars show individual rates for reaching Q4 (blue) and Q5 (green)
        - Red line shows combined Q4+Q5 mobility rate
        - Rates are shown for students from each parent income quintile
        """)
        