import pandas as pd
import numpy as np

def create_mobility_ladder(df, parent_quintile=1):
    """
    Creates mobility ladder dataframe showing probability of movement across quintiles
    for students from specified parent quintile
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    parent_quintile : int
        Parent income quintile to analyze (1-5)
    """
    # Base columns that don't change with quintile
    base_columns = [
        'name',                # College identifier
        'count',              # Number of students
        'tier',               # College tier
        'type',               # Institution type
    ]
    
    # Add parent quintile column
    parent_col = f'par_q{parent_quintile}'
    
    # Add child quintile columns for selected parent quintile
    child_cols = [f'kq{k}_cond_parq{parent_quintile}' for k in range(1, 6)]
    
    columns = base_columns + [parent_col] + child_cols
    
    mobility_df = df[columns].copy()
    
    # Convert count to integer
    mobility_df['count'] = mobility_df['count'].astype(int)
    
    # Rename columns for consistency
    mobility_df = mobility_df.rename(columns={
        parent_col: 'par_q',  # Generic parent quintile column name
        **{f'kq{k}_cond_parq{parent_quintile}': f'kq{k}_cond_parq' for k in range(1, 6)}  # Generic child quintile column names
    })
    
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