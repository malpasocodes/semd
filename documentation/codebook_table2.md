Here's a summary of the key variable groups available in the dataset:

College Identification and Classification:


super_opeid: Unique identifier for institutions/college clusters
name: College name
type: Institution type (public, private non-profit, for-profit)
tier: Selectivity classification (1-14 scale, from Ivy Plus to Not in college)
iclevel: Institution level (Four-year, Two-year, Less than Two-year)


Geographic Information:


region: Census region (Northeast, Midwest, South, West)
state: State location
cz: Commuting zone ID
county: County location


Student Demographics:


count: Average number of students per cohort
female: Fraction of female students
k_married: Fraction of students married in 2014


Mobility Metrics:


mr_kq5_pq1: Mobility rate (probability of moving from bottom quintile to top quintile)
mr_ktop1_pq1: Upper-tail mobility rate (probability of moving from bottom quintile to top 1%)


Parent Income Metrics:


par_mean: Mean parental income
par_median: Median parental income
par_rank: Mean parental income rank
par_q[1-5]: Distribution across income quintiles
par_top[X]pc: Fraction in top X percentiles


Student (Kid) Outcome Metrics:


k_rank: Mean student earnings rank
k_mean: Mean student earnings
k_median: Median student earnings
k_0inc: Fraction with zero labor earnings
k_q[1-5]: Distribution across income quintiles
k_top[X]pc: Fraction in top X percentiles


Conditional Probabilities:


k_rank_cond_parq[1-5]: Mean student rank conditional on parent quintile
kq[X]_cond_parq[Y]: Probability of student in quintile X given parent in quintile Y
ktop1pc_cond_parq[1-5]: Probability of reaching top 1% conditional on parent quintile
k_married_cond_parq[1-5]: Marriage rates conditional on parent quintile


Data Quality Indicators:


shareimputed: Share of imputed data
imputed: Indicator for any imputed data