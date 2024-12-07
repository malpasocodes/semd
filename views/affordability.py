import streamlit as st
from utils.data_utils import merge_datasets
import plotly.express as px
import pandas as pd

def show_affordability_analysis(df=None):
    """
    Show affordability analysis
    
    Parameters:
    -----------
    df : pd.DataFrame, optional
        Pre-filtered DataFrame. If None, loads and filters the data internally
    """
    # Always load merged dataset first
    df = merge_datasets()
    
    if df is not None:
        # Apply minimum Q1 filter
        min_q1_pct = st.sidebar.slider(
            "Minimum % of Bottom Quintile Students",
            min_value=0,
            max_value=20,
            value=3,
            help="Filter for colleges with at least this percentage of students from the bottom quintile"
        )
        
        df = df[df['par_q1'] * 100 >= min_q1_pct]
        
        def get_group_and_subgroup(row):
            if row['tier'] in [1, 2]:
                group = 'Elite'
                subgroup = 'Ivy Plus' if row['tier'] == 1 else 'Other Elite'
            elif row['tier'] in [3, 4]:
                group = 'Highly Selective'
                subgroup = 'Public' if row['tier'] == 3 else 'Private'
            elif row['tier'] in [5, 6]:
                group = 'Selective'
                subgroup = 'Public' if row['tier'] == 5 else 'Private'
            elif row['tier'] in [7, 8]:
                group = 'Nonselective'
                subgroup = 'Public' if row['tier'] == 7 else 'Private'
            elif row['tier'] == 10:
                group = 'Four-year for-profit'
                subgroup = 'For-profit'
            return pd.Series([group, subgroup])
        
        df[['group', 'subgroup']] = df.apply(get_group_and_subgroup, axis=1)
        df['mobility_rate'] = df['kq4_cond_parq1'] + df['kq5_cond_parq1']
        
        st.sidebar.header("Filters")
        
        global_median_price = df['sticker_price_2013'].median()
        global_median_mobility = df['mobility_rate'].median()
        
        selected_group = st.sidebar.selectbox(
            "Select Institution Group",
            ["All"] + sorted(df['group'].unique().tolist())
        )
        
        if selected_group != "All":
            plot_df = df[df['group'] == selected_group].copy()
        else:
            plot_df = df.copy()

        x_min = df['sticker_price_2013'].min()
        x_max = df['sticker_price_2013'].max()
        y_min = 0
        y_max = df['mobility_rate'].max() * 1.1

        fig = px.scatter(
            plot_df,
            x='sticker_price_2013',
            y='mobility_rate',
            color='subgroup',
            size='par_q1',
            size_max=25,
            hover_name='name',
            labels={
                'sticker_price_2013': 'Sticker Price ($)',
                'mobility_rate': 'Mobility Rate (Q4 + Q5)',
                'subgroup': 'Institution Type',
                'par_q1': 'Q1 Students'
            },
            title=f"Mobility vs Affordability - {selected_group}"
        )
        
        fig.add_hline(y=global_median_mobility, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=global_median_price, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.add_annotation(
            text="<b>High Mobility<br>Low Cost</b>",
            x=global_median_price - (global_median_price - x_min) * 0.7,
            y=global_median_mobility + (y_max - global_median_mobility) * 0.7,
            showarrow=False,
            font=dict(size=14, color="black"),
            align='left'
        )
        fig.add_annotation(
            text="<b>High Mobility<br>High Cost</b>",
            x=global_median_price + (x_max - global_median_price) * 0.7,
            y=global_median_mobility + (y_max - global_median_mobility) * 0.7,
            showarrow=False,
            font=dict(size=14, color="black"),
            align='right'
        )
        fig.add_annotation(
            text="<b>Low Mobility<br>Low Cost</b>",
            x=global_median_price - (global_median_price - x_min) * 0.7,
            y=global_median_mobility * 0.3,
            showarrow=False,
            font=dict(size=14, color="black"),
            align='left'
        )
        fig.add_annotation(
            text="<b>Low Mobility<br>High Cost</b>",
            x=global_median_price + (x_max - global_median_price) * 0.7,
            y=global_median_mobility * 0.3,
            showarrow=False,
            font=dict(size=14, color="black"),
            align='right'
        )
        
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
        
        fig.update_traces(
            hovertemplate="<br>".join([
                "<b>%{hovertext}</b>",
                "Sticker Price: $%{x:,.0f}",
                "Mobility Rate: %{y:.1%}",
                "Q1 Students: %{marker.size:.1%}",
                "<extra></extra>"
            ])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
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
        
        st.markdown("### Quadrant Distribution")
        q1 = len(plot_df[(plot_df['sticker_price_2013'] > global_median_price) & 
                        (plot_df['mobility_rate'] > global_median_mobility)])
        q2 = len(plot_df[(plot_df['sticker_price_2013'] < global_median_price) & 
                        (plot_df['mobility_rate'] > global_median_mobility)])
        q3 = len(plot_df[(plot_df['sticker_price_2013'] > global_median_price) & 
                        (plot_df['mobility_rate'] < global_median_mobility)])
        q4 = len(plot_df[(plot_df['sticker_price_2013'] < global_median_price) & 
                        (plot_df['mobility_rate'] < global_median_mobility)])
        
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
                display_df = high_mob_low_cost[['name', 'subgroup', 'sticker_price_2013', 'mobility_rate', 'par_q1']].copy()
                display_df = display_df.rename(columns={
                    'name': 'Institution',
                    'subgroup': 'Type',
                    'sticker_price_2013': 'Sticker Price',
                    'mobility_rate': 'Mobility Rate',
                    'par_q1': 'Q1 Students'
                })
                st.dataframe(
                    display_df.sort_values('Mobility Rate', ascending=False)
                    .reset_index(drop=True)
                    .assign(Rank=lambda x: range(1, len(x) + 1))
                    .set_index('Rank')
                    .style.format({
                        'Sticker Price': '${:,.0f}',
                        'Mobility Rate': '{:.1%}',
                        'Q1 Students': '{:.1%}'
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
                display_df = high_mob_high_cost[['name', 'subgroup', 'sticker_price_2013', 'mobility_rate', 'par_q1']].copy()
                display_df = display_df.rename(columns={
                    'name': 'Institution',
                    'subgroup': 'Type',
                    'sticker_price_2013': 'Sticker Price',
                    'mobility_rate': 'Mobility Rate',
                    'par_q1': 'Q1 Students'
                })
                st.dataframe(
                    display_df.sort_values('Mobility Rate', ascending=False)
                    .reset_index(drop=True)
                    .assign(Rank=lambda x: range(1, len(x) + 1))
                    .set_index('Rank')
                    .style.format({
                        'Sticker Price': '${:,.0f}',
                        'Mobility Rate': '{:.1%}',
                        'Q1 Students': '{:.1%}'
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
                display_df = low_mob_low_cost[['name', 'subgroup', 'sticker_price_2013', 'mobility_rate', 'par_q1']].copy()
                display_df = display_df.rename(columns={
                    'name': 'Institution',
                    'subgroup': 'Type',
                    'sticker_price_2013': 'Sticker Price',
                    'mobility_rate': 'Mobility Rate',
                    'par_q1': 'Q1 Students'
                })
                st.dataframe(
                    display_df.sort_values('Mobility Rate', ascending=False)
                    .reset_index(drop=True)
                    .assign(Rank=lambda x: range(1, len(x) + 1))
                    .set_index('Rank')
                    .style.format({
                        'Sticker Price': '${:,.0f}',
                        'Mobility Rate': '{:.1%}',
                        'Q1 Students': '{:.1%}'
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
                display_df = low_mob_high_cost[['name', 'subgroup', 'sticker_price_2013', 'mobility_rate', 'par_q1']].copy()
                display_df = display_df.rename(columns={
                    'name': 'Institution',
                    'subgroup': 'Type',
                    'sticker_price_2013': 'Sticker Price',
                    'mobility_rate': 'Mobility Rate',
                    'par_q1': 'Q1 Students'
                })
                st.dataframe(
                    display_df.sort_values('Mobility Rate', ascending=False)
                    .reset_index(drop=True)
                    .assign(Rank=lambda x: range(1, len(x) + 1))
                    .set_index('Rank')
                    .style.format({
                        'Sticker Price': '${:,.0f}',
                        'Mobility Rate': '{:.1%}',
                        'Q1 Students': '{:.1%}'
                    }),
                    use_container_width=True
                )
            else:
                st.write("No institutions in this quadrant")
