# app.py
import streamlit as st
from views.economic import show_mobility_ladder
from views.mobility import show_mobility_visualizations
from views.affordability import show_affordability_analysis
import pandas as pd

def get_page_config():
    return {
        "page_title": "College Mobility Analysis",
        "page_icon": "📚",
        "layout": "wide"
    }

def show_home():
    st.title("College Mobility Analysis Dashboard")
    st.markdown("""
    ### Understanding Intergenerational Income Mobility in Higher Education
    
    Select an analysis from the sidebar to begin exploring.
    """)

def apply_filters(df, include_inst_group=True):
    """
    Apply common filters to the dataset
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataset to filter
    include_inst_group : bool
        Whether to include institution group filter
    """
    if include_inst_group:
        # Institution group filter
        inst_groups = {
            "All": None,
            "Public": "Public",
            "Private Non-Profit": "Private",
            "For-Profit": "For Profit"
        }
        
        selected_group = st.sidebar.selectbox(
            "Institution Group",
            options=list(inst_groups.keys())
        )
        
        # Filter by institution group if not "All"
        if selected_group != "All":
            df = df[df['type'] == inst_groups[selected_group]]
    
    # Minimum percentage of bottom quintile students
    min_q1_pct = st.sidebar.slider(
        "Minimum % of Bottom Quintile Students",
        min_value=0,
        max_value=20,
        value=3,
        help="Filter for colleges with at least this percentage of students from the bottom quintile"
    )
    
    # Apply Q1 percentage filter
    df = df[df['par_q1'] * 100 >= min_q1_pct]
    
    return df

def main():
    st.set_page_config(**get_page_config())
    
    # First level: Category Selection
    category = st.sidebar.selectbox(
        "Select Category",
        ["Home", "Mobility Ladder", "Mobility vs Affordability"]
    )
    
    if category == "Home":
        show_home()
        return
    
    # Define navigation structure
    nav_structure = {
        "Mobility Ladder": {
            "Four Year College": [
                "Cumulative Probability",
                "Individual Probability",
                "Mobility Transitions"
            ],
        },
        "Mobility vs Affordability": {
            "Four Year College": ["Mobility vs Affordability Quadrant", "Cost Trends"],
        }
    }
    
    # Second level: Analysis Group Selection
    analysis_groups = list(nav_structure[category].keys())
    analysis_group = st.sidebar.selectbox(
        "Select Analysis Group",
        analysis_groups
    )
    
    # Third level: Analysis Selection
    analyses = nav_structure[category][analysis_group]
    analysis = st.sidebar.selectbox(
        "Select Analysis",
        analyses
    )
    
    # Route to appropriate view based on selections
    if category == "Mobility Ladder":
        # Load data once
        df = pd.read_csv("data/mrc_table2.csv")
        df = df[df['iclevel'] == 1]  # Filter for 4-year colleges
        
        # Apply filters without institution group
        filtered_df = apply_filters(df, include_inst_group=False)
        
        if analysis_group == "Four Year College":
            if analysis == "Cumulative Probability":
                show_mobility_ladder(filtered_df, "cumulative")
            elif analysis == "Individual Probability":
                show_mobility_ladder(filtered_df, "individual")
            elif analysis == "Mobility Transitions":
                show_mobility_ladder(filtered_df, "transitions")
        else:
            st.info("This analysis is currently under development.")
            
    elif category == "Mobility vs Affordability":
        if analysis == "Mobility vs Affordability Quadrant":
            # Let the affordability view handle its own data loading and filtering
            show_affordability_analysis()
        else:
            st.info("This analysis is currently under development.")

if __name__ == "__main__":
    main()
