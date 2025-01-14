import pandas as pd
import numpy as np

def calculate_mobility_work(df):
    """
    Calculate institutional mobility work including all upward mobility
    
    The formula considers:
    1. Success Rates: Movement to each higher quintile, weighted by jump size
    2. Starting Disadvantage: Proportion of Q1 students enrolled
    3. Extra Weight: Additional credit for higher Q1 enrollment (log scaled)
    """
    # Calculate weighted success rate with different weights for different jumps
    weighted_success = (
        df['kq2_cond_parq1'] * 1 +    # Moving up 1 quintile (Q1->Q2)
        df['kq3_cond_parq1'] * 2 +    # Moving up 2 quintiles (Q1->Q3)
        df['kq4_cond_parq1'] * 3 +    # Moving up 3 quintiles (Q1->Q4)
        df['kq5_cond_parq1'] * 4      # Moving up 4 quintiles (Q1->Q5)
    )
    
    # Calculate mobility work
    df['mobility_work'] = (
        weighted_success *              # Weighted success rate
        df['par_q1'] *                 # Starting disadvantage
        (1 + np.log1p(df['par_q1'] * 100))  # Extra weight for higher % of disadvantaged students
    )
    
    # Scale metrics for readability
    df['mobility_work'] = df['mobility_work'] * 100
    
    return df