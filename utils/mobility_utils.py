import pandas as pd
import numpy as np

def create_mobility_ladder(df):
    """
    Creates mobility ladder dataframe showing probability of movement across quintiles
    for students from bottom quintile families
    """
    columns = [
        'name',                # College identifier
        'count',              # Number of students
        'tier',               # College tier
        'type',               # Institution type
        'par_q1',            # Percent of students from bottom quintile
        'kq1_cond_parq1',     # Stayed in Q1
        'kq2_cond_parq1',     # Moved to Q2
        'kq3_cond_parq1',     # Moved to Q3
        'kq4_cond_parq1',     # Moved to Q4
        'kq5_cond_parq1'      # Moved to Q5
    ]
    
    mobility_df = df[columns].copy()
    
    # Convert count to integer
    mobility_df['count'] = mobility_df['count'].astype(int)
    
    return mobility_df

def get_top_mobility_colleges(mobility_df: pd.DataFrame, 
                            target_quintile: int,
                            top_n: int = 10) -> pd.DataFrame:
    """
    Get the top N colleges by mobility rate to a specific quintile.
    
    Parameters:
    -----------
    mobility_df : pd.DataFrame
        Output from create_mobility_ladder function
    target_quintile : int
        Quintile to analyze (1-5)
    top_n : int
        Number of top colleges to return
        
    Returns:
    --------
    pd.DataFrame
        Top N colleges by mobility rate to target quintile
    """
    quintile_col = f'Q{target_quintile}_Pct'
    return mobility_df.nlargest(top_n, quintile_col) 