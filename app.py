# app.py
import streamlit as st
from views.economic import show_mobility_ladder
from views.affordability import show_affordability_analysis

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

def main():
    st.set_page_config(**get_page_config())
    
    level_1 = st.sidebar.selectbox(
        "Select Category",
        ["Home", "Mobility vs Affordability",  "Mobility Ladder"]
    )
    
    if level_1 == "Home":
        show_home()
        return
    
    pages = {
        "Economic Mobility": ["Mobility Ladder", "Documentation"],
        "Mobility vs Affordability": ["Four Year Colleges", "Documentation"]
    }
    
    selected_page = st.sidebar.selectbox(
        "Select Analysis",
        pages[level_1]
    )
    
    if level_1 == "Economic Mobility":
        if selected_page == "Mobility Ladder":
            show_mobility_ladder()
        else:
            st.info("This analysis is currently under development.")
    elif level_1 == "Mobility vs Affordability":
        if selected_page == "Four Year Colleges":
            show_affordability_analysis()
    else:
        st.info("This analysis is currently under development.")

if __name__ == "__main__":
    main()
