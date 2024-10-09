import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('corrected_version.csv')

# Define a dictionary to map integers to their corresponding labels
severity_mapping = {1: 'Killed', 2: 'Severe', 3: 'Slight'}

# Replace values in the 'casualty_severity' column using the mapping
df['accident_severity'] = df['accident_severity'].map(severity_mapping)

# Save the modified DataFrame back to a CSV file
df.to_csv('2022_fixed2.csv', index=False)
