import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def show_mobility_work_analysis(df):
    """
    Show analysis of institutional mobility work
    """
    st.title("Institutional Mobility Work Analysis")
    
    st.markdown("""
    This analysis quantifies the 'work done' by institutions in promoting economic mobility.
    The model considers:
    - Success rate (Q4+Q5 mobility)
    - Initial disadvantage (% of students from bottom quintile)
    - Extra weight for institutions serving more disadvantaged students
    """)
    
    # Calculate work metrics
    from utils.stats_models import calculate_mobility_work
    df_work = calculate_mobility_work(df)
    
    # Calculate average mobility score
    df_work['avg_mobility_score'] = (
        df_work['kq2_cond_parq1'] + 
        df_work['kq3_cond_parq1'] + 
        df_work['kq4_cond_parq1'] + 
        df_work['kq5_cond_parq1']
    ) * 25
    
    # Create institution type grouping
    def get_institution_type(row):
        if row['tier'] in [1, 2]:
            return 'Elite Private'
        elif row['tier'] in [3]:
            return 'Highly Selective Public'
        elif row['tier'] in [4]:
            return 'Highly Selective Private'
        elif row['tier'] in [5]:
            return 'Selective Public'
        elif row['tier'] in [6]:
            return 'Selective Private'
        else:
            return 'Other'
    
    df_work['institution_type'] = df_work.apply(get_institution_type, axis=1)
    
    # Add institution type selection to sidebar
    st.sidebar.markdown("### Compare Institution Types")
    
    institution_types = ['Elite Private', 'Highly Selective Public', 
                        'Highly Selective Private', 'Selective Public', 
                        'Selective Private', 'Other']
    
    type1 = st.sidebar.selectbox(
        "First Institution Type",
        options=institution_types,
        key='type1'
    )
    
    remaining_types = [t for t in institution_types if t != type1]
    type2 = st.sidebar.selectbox(
        "Second Institution Type",
        options=remaining_types,
        key='type2'
    )
    
    # Filter data for selected types
    df_type1 = df_work[df_work['institution_type'] == type1]
    df_type2 = df_work[df_work['institution_type'] == type2]
    
    # Calculate combined Q1-Q4 enrollment for each filtered dataset
    df_type1['bottom_80_pct'] = (
        df_type1['par_q1'] + 
        df_type1['par_q2'] + 
        df_type1['par_q3'] + 
        df_type1['par_q4']
    )
    
    df_type2['bottom_80_pct'] = (
        df_type2['par_q1'] + 
        df_type2['par_q2'] + 
        df_type2['par_q3'] + 
        df_type2['par_q4']
    )
    
    # Combine selected data for visualizations
    df_selected = pd.concat([df_type1, df_type2])
    
    # Create visualizations with filtered data
    st.subheader("Mobility Work Comparison")
    
    # Box plot of mobility work
    fig1 = px.box(
        df_selected,
        x='institution_type',
        y='mobility_work',
        title="Distribution of Mobility Work",
        labels={
            'institution_type': 'Institution Type',
            'mobility_work': 'Mobility Work Score'
        }
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Scatter plot comparing mobility work vs sticker price
    fig2 = go.Figure()
    
    # Add traces for each institution type
    fig2.add_trace(go.Scatter(
        x=df_type1['sticker_price_2013'],
        y=df_type1['mobility_work'],
        mode='markers',
        name=type1,
        marker=dict(color='#1f77b4'),
        text=df_type1['name'],
        hovertemplate="<br>".join([
            "Institution: %{text}",
            "Sticker Price: $%{x:,.0f}",
            "Work Score: %{y:.1f}",
            "<extra></extra>"
        ])
    ))
    
    fig2.add_trace(go.Scatter(
        x=df_type2['sticker_price_2013'],
        y=df_type2['mobility_work'],
        mode='markers',
        name=type2,
        marker=dict(color='#2ca02c'),
        text=df_type2['name'],
        hovertemplate="<br>".join([
            "Institution: %{text}",
            "Sticker Price: $%{x:,.0f}",
            "Work Score: %{y:.1f}",
            "<extra></extra>"
        ])
    ))
    
    fig2.update_layout(
        title=f"Mobility Work vs Sticker Price",
        xaxis_title="Sticker Price ($)",
        yaxis_title="Mobility Work Score",
        height=600,
        xaxis=dict(tickformat="$,.0f")  # Format x-axis ticks as currency
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Show summary statistics side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"{type1} Statistics")
        st.metric("Number of Institutions", len(df_type1))
        st.metric("Average Mobility Work", f"{df_type1['mobility_work'].mean():.1f}")
        st.metric("Average Mobility Score", f"{df_type1['avg_mobility_score'].mean():.1f}%")
        st.metric("Average Q1-Q4 Enrollment", f"{df_type1['bottom_80_pct'].mean() * 100:.1f}%")
        
        # Show top 10 institutions
        st.markdown(f"#### Top 10 {type1} Institutions")
        top10_1 = df_type1.nlargest(10, 'mobility_work')[
            ['name', 'mobility_work', 'avg_mobility_score', 'bottom_80_pct']
        ].copy()
        top10_1['bottom_80_pct'] = top10_1['bottom_80_pct'] * 100
        st.dataframe(
            top10_1.style.format({
                'mobility_work': '{:.1f}',
                'avg_mobility_score': '{:.1f}%',
                'bottom_80_pct': '{:.1f}%'
            }).set_properties(**{'text-align': 'left'})
        )
    
    with col2:
        st.subheader(f"{type2} Statistics")
        st.metric("Number of Institutions", len(df_type2))
        st.metric("Average Mobility Work", f"{df_type2['mobility_work'].mean():.1f}")
        st.metric("Average Mobility Score", f"{df_type2['avg_mobility_score'].mean():.1f}%")
        st.metric("Average Q1-Q4 Enrollment", f"{df_type2['bottom_80_pct'].mean() * 100:.1f}%")
        
        # Show top 10 institutions
        st.markdown(f"#### Top 10 {type2} Institutions")
        top10_2 = df_type2.nlargest(10, 'mobility_work')[
            ['name', 'mobility_work', 'avg_mobility_score', 'bottom_80_pct']
        ].copy()
        top10_2['bottom_80_pct'] = top10_2['bottom_80_pct'] * 100
        st.dataframe(
            top10_2.style.format({
                'mobility_work': '{:.1f}',
                'avg_mobility_score': '{:.1f}%',
                'bottom_80_pct': '{:.1f}%'
            }).set_properties(**{'text-align': 'left'})
        ) 