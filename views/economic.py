import streamlit as st
from utils.data_utils import load_mobility_data
from utils.viz_utils import plot_mobility_ladder

def show_mobility_ladder():
    df = load_mobility_data()
    
    if df is not None:
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
            10: "Four-year for-profit"

        }
        
        # Add minimum Q1 students filter
        min_q1_pct = st.sidebar.slider(
            "Minimum % of Q1 Students",
            min_value=0,
            max_value=50,  # Adjust max as needed
            value=5,
            step=1,
            help="Filter institutions by minimum percentage of students from bottom quintile"
        )
        
        st.sidebar.markdown("---")  # Add separator
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            tier1 = st.selectbox("Select First Tier", 
                               options=["All"] + list(tier_map.values()), 
                               key='tier1')
        with col2:
            remaining_tiers = ["All"] + [t for t in tier_map.values() if t != tier1]
            tier2 = st.selectbox("Select Second Tier", 
                               options=remaining_tiers, 
                               key='tier2')
        
        # Pre-filter the dataframe based on Q1 percentage
        filtered_df = df[df['par_q1'] * 100 >= min_q1_pct].copy()
        
        if len(filtered_df) > 0:
            # Create and display plots
            fig_line, fig_bar, college_data = plot_mobility_ladder(filtered_df, tier1, tier2)
            
            # Display both plots
            st.plotly_chart(fig_line, use_container_width=True)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Display institution lists
            st.markdown("### Institutions by Tier")
            st.markdown(f"*Showing institutions with {min_q1_pct}% or more students from bottom quintile*")
            
            tab1, tab2 = st.tabs([tier1, tier2])
            
            with tab1:
                display_df = college_data[tier1].copy()
                display_df['Q1 Students %'] = display_df['par_q1'] * 100
                display_df['Q4/Q5 Mobility %'] = (display_df['kq4_cond_parq1'] + display_df['kq5_cond_parq1']) * 100
                
                st.dataframe(
                    display_df[['name', 'Q1 Students %', 'Q4/Q5 Mobility %']]
                    .sort_values('Q4/Q5 Mobility %', ascending=False)
                    .style.format({
                        'Q1 Students %': '{:.1f}%',
                        'Q4/Q5 Mobility %': '{:.1f}%'
                    }),
                    use_container_width=True
                )
            
            with tab2:
                display_df = college_data[tier2].copy()
                display_df['Q1 Students %'] = display_df['par_q1'] * 100
                display_df['Q4/Q5 Mobility %'] = (display_df['kq4_cond_parq1'] + display_df['kq5_cond_parq1']) * 100
                
                st.dataframe(
                    display_df[['name', 'Q1 Students %', 'Q4/Q5 Mobility %']]
                    .sort_values('Q4/Q5 Mobility %', ascending=False)
                    .style.format({
                        'Q1 Students %': '{:.1f}%',
                        'Q4/Q5 Mobility %': '{:.1f}%'
                    }),
                    use_container_width=True
                )
        else:
            st.warning(f"No institutions have {min_q1_pct}% or more students from the bottom quintile. Try lowering the threshold.")