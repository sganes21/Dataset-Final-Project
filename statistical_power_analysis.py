## Statistical Power Analysis 

import statsmodels.stats.power as smp

# Define parameters
effect_size = (0.2)  # Example effect size
alpha = (0.01)       # Significance level
power = 0.80       # Desired power

# Create a power analysis object
analysis = smp.TTestIndPower()

# Calculate sample size
sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, alternative='two-sided')
print(f"Required sample size from power analysis: {sample_size}")