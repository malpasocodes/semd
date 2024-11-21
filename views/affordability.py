
import streamlit as st
from utils.data_utils import merge_datasets
import plotly.express as px
import pandas as pd

def show_affordability_analysis():
    # Use merge_datasets instead of just load_mobility_data
    df = merge_datasets()
    
    if df is not None:
        # Create new grouping categories
        def get_group_and_subgroup(row):
            if row['tier'] in [1, 2]:  # Elite
                group = 'Elite'
                subgroup = 'Ivy Plus' if row['tier'] == 1 else 'Other Elite'
            elif row['tier'] in [3, 4]:  # Highly Selective
                group = 'Highly Selective'
                subgroup = 'Public' if row['tier'] == 3 else 'Private'
            elif row['tier'] in [5, 6]:  # Selective
                group = 'Selective'
                subgroup = 'Public' if row['tier'] == 5 else 'Private'
            elif row['tier'] in [7, 8]:  # Nonselective
                group = 'Nonselective'
                subgroup = 'Public' if row['tier'] == 7 else 'Private'
            elif row['tier'] == 10:  # For-profit
                group = 'Four-year for-profit'
                subgroup = 'For-profit'
            return pd.Series([group, subgroup])
        
        # Add group and subgroup columns
        df[['group', 'subgroup']] = df.apply(get_group_and_subgroup, axis=1)
        
        # Calculate mobility rate (Q4 + Q5)
        df['mobility_rate'] = df['kq4_cond_parq1'] + df['kq5_cond_parq1']
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Add Q1 enrollment filter
        min_q1_pct = st.sidebar.slider(
            "Minimum % of Q1 Students",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
            help="Filter institutions by minimum percentage of students from bottom quintile"
        )
        
        # Apply Q1 filter
        df = df[df['par_q1'] * 100 >= min_q1_pct]
        
        # Calculate global medians after Q1 filter but before group selection
        global_median_price = df['sticker_price_2013'].median()
        global_median_mobility = df['mobility_rate'].median()
        
        selected_group = st.sidebar.selectbox(
            "Select Institution Group",
            ["All"] + sorted(df['group'].unique().tolist())
        )
        
        # Filter data based on selection
        if selected_group != "All":
            plot_df = df[df['group'] == selected_group].copy()
        else:
            plot_df = df.copy()

        # Create scatter plot
        fig = px.scatter(
            plot_df,
            x='sticker_price_2013',
            y='mobility_rate',
            color='subgroup',
            hover_name='name',
            labels={
                'sticker_price_2013': 'Sticker Price ($)',
                'mobility_rate': 'Mobility Rate (Q4 + Q5)',
                'subgroup': 'Institution Type'
            },
            title=f"Mobility vs Affordability - {selected_group} (Global Medians)"
        )
        
        # Add quadrant lines using global medians
        fig.add_hline(y=global_median_mobility, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=global_median_price, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Calculate fixed ranges based on full dataset
        x_min = df['sticker_price_2013'].min()
        x_max = df['sticker_price_2013'].max()
        y_min = 0
        y_max = df['mobility_rate'].max() * 1.1
        
        # Add quadrant labels with absolute positioning
        fig.add_annotation(  # Top Left - Low Cost
            text="<b>High Mobility<br>Low Cost</b>",
            x=global_median_price - (global_median_price - x_min) * 0.7,
            y=global_median_mobility + (y_max - global_median_mobility) * 0.7,
            showarrow=False,
            font=dict(size=14, color="black"),
            align='left'
        )
        fig.add_annotation(  # Top Right - High Cost
            text="<b>High Mobility<br>High Cost</b>",
            x=global_median_price + (x_max - global_median_price) * 0.7,
            y=global_median_mobility + (y_max - global_median_mobility) * 0.7,
            showarrow=False,
            font=dict(size=14, color="black"),
            align='right'
        )
        fig.add_annotation(  # Bottom Left - Low Cost
            text="<b>Low Mobility<br>Low Cost</b>",
            x=global_median_price - (global_median_price - x_min) * 0.7,
            y=global_median_mobility * 0.3,
            showarrow=False,
            font=dict(size=14, color="black"),
            align='left'
        )
        fig.add_annotation(  # Bottom Right - High Cost
            text="<b>Low Mobility<br>High Cost</b>",
            x=global_median_price + (x_max - global_median_price) * 0.7,
            y=global_median_mobility * 0.3,
            showarrow=False,
            font=dict(size=14, color="black"),
            align='right'
        )
        
        # Update layout with fixed ranges
        fig.update_layout(
            xaxis=dict(
                tickformat='$,.0f',
                autorange='reversed',
                range=[x_max * 1.02, x_min * 0.98],
            ),
            yaxis=dict(
                tickformat='.0%',
                range=[y_min, y_max]
            ),
            height=800,
            width=1200,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(l=50, r=50, t=50, b=50),
            autosize=False
        )
        
        # Add hover template
        fig.update_traces(
            hovertemplate="<br>".join([
                "<b>%{hovertext}</b>",
                "Sticker Price: $%{x:,.0f}",
                "Mobility Rate: %{y:.1%}",
                "<extra></extra>"
            ])
        )
        
        # Display plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced summary statistics with quadrant information
        st.markdown("### Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Number of Institutions", len(plot_df))
        with col2:
            st.metric("Global Median Sticker Price", 
                     f"${global_median_price:,.0f}")
        with col3:
            st.metric("Global Median Mobility Rate", 
                     f"{global_median_mobility:.1%}")
        
        # Add quadrant analysis using global medians
        st.markdown("### Quadrant Distribution")
        q1 = len(plot_df[(plot_df['sticker_price_2013'] > global_median_price) & 
                        (plot_df['mobility_rate'] > global_median_mobility)])  # High mobility, High cost
        q2 = len(plot_df[(plot_df['sticker_price_2013'] < global_median_price) & 
                        (plot_df['mobility_rate'] > global_median_mobility)])  # High mobility, Low cost
        q3 = len(plot_df[(plot_df['sticker_price_2013'] > global_median_price) & 
                        (plot_df['mobility_rate'] < global_median_mobility)])  # Low mobility, High cost
        q4 = len(plot_df[(plot_df['sticker_price_2013'] < global_median_price) & 
                        (plot_df['mobility_rate'] < global_median_mobility)])  # Low mobility, Low cost
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **High Cost Region:**
            - High Mobility: {q1} institutions
            - Low Mobility: {q3} institutions
            """)
        with col2:
            st.markdown(f"""
            **Low Cost Region:**
            - High Mobility: {q2} institutions
            - Low Mobility: {q4} institutions
            """)

        # Add institution lists using global medians
        st.markdown("### Institution Lists by Quadrant")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "High Mobility, Low Cost", 
            "High Mobility, High Cost",
            "Low Mobility, Low Cost",
            "Low Mobility, High Cost"
        ])
        
        with tab1:
            high_mob_low_cost = plot_df[
                (plot_df['sticker_price_2013'] < global_median_price) & 
                (plot_df['mobility_rate'] > global_median_mobility)
            ].copy()
            
            if not high_mob_low_cost.empty:
                display_df = high_mob_low_cost[['name', 'subgroup', 'sticker_price_2013', 'mobility_rate']].copy()
                display_df = display_df.rename(columns={
                    'name': 'Institution',
                    'subgroup': 'Type',
                    'sticker_price_2013': 'Sticker Price',
                    'mobility_rate': 'Mobility Rate'
                })
                st.dataframe(
                    display_df.sort_values('Mobility Rate', ascending=False)
                    .reset_index(drop=True)
                    .assign(Rank=lambda x: range(1, len(x) + 1))
                    .set_index('Rank')
                    .style.format({
                        'Sticker Price': '${:,.0f}',
                        'Mobility Rate': '{:.1%}'
                    }),
                    use_container_width=True
                )
            else:
                st.write("No institutions in this quadrant")
        
        with tab2:
            high_mob_high_cost = plot_df[
                (plot_df['sticker_price_2013'] > global_median_price) & 
                (plot_df['mobility_rate'] > global_median_mobility)
            ].copy()
            
            if not high_mob_high_cost.empty:
                display_df = high_mob_high_cost[['name', 'subgroup', 'sticker_price_2013', 'mobility_rate']].copy()
                display_df = display_df.rename(columns={
                    'name': 'Institution',
                    'subgroup': 'Type',
                    'sticker_price_2013': 'Sticker Price',
                    'mobility_rate': 'Mobility Rate'
                })
                st.dataframe(
                    display_df.sort_values('Mobility Rate', ascending=False)
                    .reset_index(drop=True)
                    .assign(Rank=lambda x: range(1, len(x) + 1))
                    .set_index('Rank')
                    .style.format({
                        'Sticker Price': '${:,.0f}',
                        'Mobility Rate': '{:.1%}'
                    }),
                    use_container_width=True
                )
            else:
                st.write("No institutions in this quadrant")
        
        with tab3:
            low_mob_low_cost = plot_df[
                (plot_df['sticker_price_2013'] < global_median_price) & 
                (plot_df['mobility_rate'] < global_median_mobility)
            ].copy()
            
            if not low_mob_low_cost.empty:
                display_df = low_mob_low_cost[['name', 'subgroup', 'sticker_price_2013', 'mobility_rate']].copy()
                display_df = display_df.rename(columns={
                    'name': 'Institution',
                    'subgroup': 'Type',
                    'sticker_price_2013': 'Sticker Price',
                    'mobility_rate': 'Mobility Rate'
                })
                st.dataframe(
                    display_df.sort_values('Mobility Rate', ascending=False)
                    .reset_index(drop=True)
                    .assign(Rank=lambda x: range(1, len(x) + 1))
                    .set_index('Rank')
                    .style.format({
                        'Sticker Price': '${:,.0f}',
                        'Mobility Rate': '{:.1%}'
                    }),
                    use_container_width=True
                )
            else:
                st.write("No institutions in this quadrant")
        
        with tab4:
            low_mob_high_cost = plot_df[
                (plot_df['sticker_price_2013'] > global_median_price) & 
                (plot_df['mobility_rate'] < global_median_mobility)
            ].copy()
            
            if not low_mob_high_cost.empty:
                display_df = low_mob_high_cost[['name', 'subgroup', 'sticker_price_2013', 'mobility_rate']].copy()
                display_df = display_df.rename(columns={
                    'name': 'Institution',
                    'subgroup': 'Type',
                    'sticker_price_2013': 'Sticker Price',
                    'mobility_rate': 'Mobility Rate'
                })
                st.dataframe(
                    display_df.sort_values('Mobility Rate', ascending=False)
                    .reset_index(drop=True)
                    .assign(Rank=lambda x: range(1, len(x) + 1))
                    .set_index('Rank')
                    .style.format({
                        'Sticker Price': '${:,.0f}',
                        'Mobility Rate': '{:.1%}'
                    }),
                    use_container_width=True
                )
            else:
                st.write("No institutions in this quadrant")
