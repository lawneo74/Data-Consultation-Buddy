import panda as pd
import json

# Read the Excel file
excel_data_df = pd.read_excel('./data/Mock Metadata Catalogue.xlsv',sheet_name='Sheet1')

# Create dictionary
json_data = {}

for _, row in excel_data_df.iloc[1:].iterrows():
    dataset_id = row['Dataset']
    dataset_details = {
        'Dataset': row['Dataset'],
        'Description': row['Description'],
        'Data Source': row['Data Source'],
        'Branch': row['Branch'],
        'Data Custodian': row['Data Custodian'],
        'Security Tag': row['Security Tag'],
        'Sensitivity Tag': row['Sensitivity Tag'],
        'Update Frequency': row['Update Frequency'],
        'Coverage Start Date': row['Coverage Start Date'],
        'Coverage End Date': row['Coverage End Date'],
        'Usage Guideline': row['Usage Guideline']
    }
    json_data[dataset_id] = dataset_details

# Convert dictionary to JSON string
json_string = json.dumps(json_data,indent=2)

print(json_string)