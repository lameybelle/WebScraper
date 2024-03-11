import pandas as pd

# Read the classified and unclassified CSV files
classified_df = pd.read_csv('CSVs/classifiedEmployees.csv', delimiter=',')
unclassified_df = pd.read_csv('CSVs/unclassifiedEmployees.csv', delimiter=',')

# Replace empty values in 'JOB END DATE' with a placeholder (e.g., 'NA')
classified_df['JOB END DATE'] = classified_df['JOB END DATE'].fillna('NA')
unclassified_df['JOB END DATE'] = unclassified_df['JOB END DATE'].fillna('NA')

# Add a "UNION STATUS" column to indicate the source file
classified_df['UNION STATUS'] = 'CLASSIFIED'
unclassified_df['UNION STATUS'] = 'UNCLASSIFIED'

# Concatenate the classified and unclassified dataframes
combined_df = pd.concat([classified_df, unclassified_df])

# Sort the dataframe by the 'LAST' column
combined_df = combined_df.sort_values(by=['LAST'])

# Combine 'FIRST' and 'LAST' into a single 'Name' column temporarily for merging
combined_df['Name'] = combined_df['FIRST'] + ' ' + combined_df['LAST']

# Read the 'findPeople_df' dataframe
classified_findPeople = pd.read_csv('CSVs/classifiedFindPeople.csv', delimiter=',')
unclassified_findPeople = pd.read_csv('CSVs/unclassifiedFindPeople.csv', delimiter=',')

# Concatenate the classified and unclassified 'findPeople_df' dataframes
findPeople_df = pd.concat([classified_findPeople, unclassified_findPeople])

# Merge the 'combined_df' and 'findPeople_df' dataframes based on the 'Name' column
merged_df = pd.merge(combined_df.copy(), findPeople_df, on='Name', how='left')

# Drop the temporarily added 'Name' column
combined_df = combined_df.drop(columns=['Name'])

# Save the merged dataframe to a new CSV file
merged_df.to_csv('CSVs/combinedWithFindPeople.csv', sep=',', index=False)

