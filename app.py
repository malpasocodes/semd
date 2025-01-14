# app.py
import streamlit as st
from views.economic import show_mobility_ladder, show_data_verification
from views.mobility import show_mobility_visualizations
from views.affordability import show_affordability_analysis
from views.institution import show_institution_profile
from views.enrollment import show_enrollment_patterns
import pandas as pd

def get_page_config():
    return {
        "page_title": "College Mobility Analysis",
        "page_icon": "📚",
        "layout": "wide"
    }

def show_home():
    st.title("College Mobility Analysis Dashboard")
    
    # Main description
    st.markdown("""
    ### Understanding Intergenerational Income Mobility in Higher Education
    
    This interactive dashboard explores how different colleges and universities contribute to intergenerational 
    income mobility. Using data from [Opportunity Insights](https://opportunityinsights.org/), we analyze how students from different 
    income backgrounds fare after attending specific institutions, with a particular focus on the relationship 
    between mobility outcomes and college affordability.
    """)
    
    # Navigation guide
    st.markdown("""
    ### Using the Dashboard
    
    Use the sidebar on the left to navigate through different analyses:
    
    1. **Select Category** - Choose between:
       - *Mobility Ladder*: Examine how students from a specific parent income quintile move across income quintiles
       - *Mobility vs Affordability*: Explore the relationship between mobility rates and college costs
    
    2. **Select Analysis Group** - Currently focused on four-year colleges
    
    3. **Select Analysis** - Choose specific visualizations and analyses within each category
    
    Additional filters and settings will appear in the sidebar based on your selections, allowing you to 
    customize the analysis for specific institution types and student populations.
    """)
    
    # Add cautionary note at the bottom
    st.markdown("---")  # Add a horizontal line for separation
    st.warning("""
    **⚠️ Note:** This website is currently under construction and active development. 
    The data and analyses are being verified and validated. Please use the results with caution 
    and refer to [Opportunity Insights](https://opportunityinsights.org/) for the official data and documentation.
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
        value=0,
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
        ["Home", "Mobility Ladder", "Mobility vs Affordability", "Institution Explorer", "Enrollment Explorer", "Mobility Work"]
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
                "Data Verification"
            ],
        },
        "Mobility vs Affordability": {
            "Four Year College": ["Mobility vs Affordability Quadrant", "Cost Trends"],
        },
        "Institution Explorer": {
            "Four Year College": ["Institution Profile", "Peer Comparison"]
        },
        "Enrollment Explorer": {
            "Four Year College": ["Enrollment Patterns"]
        },
        "Mobility Work": {
            "Four Year College": ["Work Analysis"]
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
        
        # Filter for 4-year colleges
        df = df[df['iclevel'] == 1]
        
        # Apply filters without institution group
        filtered_df = apply_filters(df, include_inst_group=False)
        
        if analysis_group == "Four Year College":
            # Add parent quintile selection
            st.sidebar.markdown("### Analysis Settings")
            selected_quintile = st.sidebar.selectbox(
                "Select Parent Income Quintile",
                ["Q1", "Q2", "Q3", "Q4", "Q5"],
                index=0
            )
            quintile_num = int(selected_quintile[1])
            
            if analysis == "Data Verification":
                show_data_verification(filtered_df, quintile_num)
            elif analysis == "Cumulative Probability":
                show_mobility_ladder(filtered_df, "cumulative", parent_quintile=quintile_num)
            elif analysis == "Individual Probability":
                show_mobility_ladder(filtered_df, "individual", parent_quintile=quintile_num)
        else:
            st.info("This analysis is currently under development.")
            
    elif category == "Mobility vs Affordability":
        # Load and merge datasets
        from utils.data_utils import merge_datasets
        df = merge_datasets()
        
        if df is not None:  # Check if merge was successful
            if analysis == "Mobility vs Affordability Quadrant":
                # Add parent quintile selection
                st.sidebar.markdown("### Analysis Settings")
                selected_quintile = st.sidebar.selectbox(
                    "Select Parent Income Quintile",
                    ["Q1", "Q2", "Q3", "Q4", "Q5"],
                    index=0
                )
                quintile_num = int(selected_quintile[1])
                
                show_affordability_analysis(df, parent_quintile=quintile_num)
            else:
                st.info("This analysis is currently under development.")
        else:
            st.error("Error loading data. Please check the data files.")
    elif category == "Institution Explorer":
        # Load and merge datasets
        from utils.data_utils import merge_datasets
        df = merge_datasets()
        
        if df is not None:  # Check if merge was successful
            if analysis == "Institution Profile":
                show_institution_profile(df)
            else:
                st.info("This analysis is currently under development.")
        else:
            st.error("Error loading data. Please check the data files.")
    elif category == "Enrollment Explorer":
        # Load data
        df = pd.read_csv("data/mrc_table2.csv")
        df = df[df['iclevel'] == 1]  # Filter for 4-year colleges
        
        if analysis == "Enrollment Patterns":
            show_enrollment_patterns(df)
        else:
            st.info("This analysis is currently under development.")
    elif category == "Mobility Work":
        # Load and merge datasets
        from utils.data_utils import merge_datasets
        df = merge_datasets()
        
        if df is not None:
            if analysis == "Work Analysis":
                from views.mobility_work import show_mobility_work_analysis
                show_mobility_work_analysis(df)
            else:
                st.info("This analysis is currently under development.")
        else:
            st.error("Error loading data. Please check the data files.")

if __name__ == "__main__":
    main()
