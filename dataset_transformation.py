# # Dataset Project
# 
# **Author:** Santosh Ganesan
# 
# **Date:** 26 November 2024
# 
# Sections of this code were modified from https://www.kaggle.com/code/bachkhoa144/georgia-animal-shelter-eda-time-series-forecast
# See Acknowledgements section in README.md for more information.

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc
from math import pi

## Defining Functions

# Understanding the Datatypes of the Columns (Georgia Shelter Database)

def get_detailed_dtypes(df):
    detailed_dtypes = {}
    for column in df.columns:
        # Get unique types
        unique_types = df[column].apply(type).value_counts().to_dict()
        
        # Get pandas dtype
        pandas_dtype = str(df[column].dtype)
        
        # Check for NaN values
        nan_count = df[column].isna().sum()
        
        # Get unique values (for categorical-like columns)
        unique_values = df[column].nunique()
        
        # Combine information
        detailed_dtypes[column] = {
            'pandas_dtype': pandas_dtype,
            'python_types': unique_types,
            'nan_count': nan_count,
            'unique_values': unique_values
        }
    
    return detailed_dtypes

# Converting Report Period End to Data Year 

def copy_year(report_period_end, data_year):
    if pd.notnull(report_period_end):
        data_year = pd.to_datetime(report_period_end).year
    return data_year

# Function to replace string "NaN" with 0, leave other values unchanged
def replace_nan_string(value):
    if isinstance(value, str) and value.lower() == "nan":
        return 0
    return value


def main():

    # Suppress specific warnings from pandas
    pd.options.mode.chained_assignment = None

    # Suppress warnings general warnings from pandas
    import warnings
    warnings.filterwarnings('ignore')

    # Load the data from the Georgia Animal Shelter Database
    from dataset_source import load_data

    # URL of the Excel file
    url = "https://agr.georgia.gov/sites/default/files/documents/pets-and-livestock/shelter-report-data-export-october-2024.xlsx.xlsx"

    ## Load the data
    df_georgia_database = load_data(url)

    # Check if data was successfully loaded
    if df_georgia_database is not None:
        print(df_georgia_database.head())  # Display the first few rows of the DataFrame
    else:
        print("Failed to load data.")

    # Loading Shelter Name Annotations
    df_annotations=pd.read_excel('shelter-report-data-export-october-2024_annotations_master.xlsx')

    # Loading Best Friends Animal Society Database
    df2=pd.read_excel('Data Request-Ganesan.xlsx')

    # Reset the index
    df2.reset_index(drop=True, inplace=True)

    # Display the DataFrame
    pd.set_option('display.max_columns', None)


    ## Cleaning the data

    # Parsing Georgia Animal Shelter Database
    headers = df_georgia_database.iloc[2]
    df_georgia_database = pd.DataFrame(df_georgia_database.values[3:], columns=headers)

    # Reset the index
    df_georgia_database.reset_index(drop=True, inplace=True)

    # Display the DataFrame
    pd.set_option('display.max_columns', None)

    df_georgia_database = df_georgia_database.iloc[:, 1:].reset_index(drop=True)
    df_georgia_database.dropna(axis=1, how='all', inplace=True)




    # Get the detailed dtype information
    detailed_info = get_detailed_dtypes(df_georgia_database)

    # Transform the Object Types to Int Types 

    columns_to_convert = df_georgia_database.columns[4:]

    for col in columns_to_convert:
        df_georgia_database[col] = df_georgia_database[col].astype(int)
        
    # Reset the index
    df_georgia_database.reset_index(drop=True, inplace=True)

    # Get the detailed dtype information
    detailed_info = get_detailed_dtypes(df_georgia_database)


    # Merging Annotations into Georgia Animal Shelter Dataframe
    df_georgia_database = pd.concat([df_georgia_database, df_annotations['Shelter Name Annotation']], axis=1)


    # Checking the Data in Best Friends Animal Society

    ## Understanding the Datatypes of the Columns (Best Friends Animal Society)

    # Get the detailed dtype information
    detailed_info = get_detailed_dtypes(df2)


    ### Populate State Column

    # Count the number of non-empty (False) results
    non_empty_count = (~df2['State'].isnull()).sum()
    state_dtype = df2['State'].dtype


    ## Merging Georgia Animal Shelter & Best Friends Database into Combined Database

    # Merge the two DataFrames on the "Shelter Name" column
    combined_df = pd.merge(df_georgia_database, df2, on='Shelter Name', how='outer')

    # Reset the index of the new DataFrame
    combined_df = combined_df.reset_index(drop=True)



    ### Populating Data Year Column



    combined_df['Data Year'] = combined_df.apply(lambda row: copy_year(row['Report Period End'], row['Data Year']), axis=1)



    ### Populating the State Column
    combined_df['State'].fillna('GA', inplace=True)

    # Replacing NaNs with zeros in Combined Dataframe

    # Identify the affected columns
    first_33_columns = combined_df.columns[4:35].tolist()


    # Apply the function to the first 33 columns
    for column in first_33_columns:
        combined_df[column] = combined_df[column].apply(replace_nan_string)

    # Convert any remaining NaN (not string "NaN") to 0
    combined_df[first_33_columns] = combined_df[first_33_columns].fillna(0)

    # Identify the affected columns
    first_42_columns = combined_df.columns[41:].tolist()

    # Apply the function to the first 42 columns
    for column in first_42_columns:
        combined_df[column] = combined_df[column].apply(replace_nan_string)

    # Convert any remaining NaN (not string "NaN") to 0
    combined_df[first_42_columns] = combined_df[first_42_columns].fillna(0)



    ## Verifying the Datatypes of the Combined Dataframe

    # Get the detailed dtype information
    detailed_info = get_detailed_dtypes(combined_df)

    ### Handling Assumed Mistakes in Data Entry

    # Convert 'Report Period Start' to datetime for accurate indexing
    combined_df['Report Period Start'] = pd.to_datetime(combined_df['Report Period Start'])

    # Check for the outlier in September 2022
    outlier_condition = (combined_df['Report Period Start'].dt.year == 2022) & (combined_df['Report Period Start'].dt.month == 9) & (combined_df['Shelter Name'] == "DEKALB COUNTY ANIMAL SERVICES")

    # Calculate the average for September of 2020 and 2021
    september_condition = combined_df['Report Period Start'].dt.month == 9
    average = combined_df.loc[september_condition & (combined_df['Report Period Start'].dt.year != 2022), 'Canine stray at large'].mean()

    # Replace the outlier with the average
    combined_df.loc[outlier_condition, 'Canine stray at large'] = average


    ## Exploratory Data Analysis

    ### Examining Total Intakes by State

    # Filter the data for years 2021-2023
    df_filtered = combined_df[pd.to_numeric(combined_df['Data Year'], errors='coerce').between(2021, 2023)]

    # Remove Duplicate Entries
    df_filtered = df_filtered[df_filtered['Shelter Name Annotation'] != 'R']

    # Group by State and sum the relevant columns
    columns_to_sum = [
        'Canine stray at large', 'Feline stray at large',
        'Canine relinquished by owner', 'Feline relinquished by owner',
        'Canine intake owner intended euthanasia', 'Feline intake owner intended euthanasia',
        'Canine transferred in from agency', 'Feline transferred in from agency',
        'Canine other intakes', 'Feline other intakes', 'Total Intake Gross'
    ]

    state_totals = df_filtered.groupby('State')[columns_to_sum].sum().sum(axis=1).sort_values(ascending=False)

    # Create the bar plot
    plt.figure(figsize=(35, 30))
    state_totals.plot(kind='bar')

    # Customize the plot
    plt.title('Total Stray Pets by State (2021-2023)', fontsize=16)
    plt.xlabel('State', fontsize=12)
    plt.ylabel('Total Count', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Add value labels on top of each bar
    for i, v in enumerate(state_totals):
        plt.text(i, v, f'{v:,.0f}', ha='center', va='bottom')

    # Show the plot
    plt.savefig('Total_Intake_Gross.png')

    ### Examining Total Intakes by State Segregated by Dog and Cat Animal Type

    # Remove Duplicate Entries
    df_filtered = df_filtered[df_filtered['Shelter Name Annotation'] != 'R']

    # Define column names for dogs and cats
    dog_columns = ['Canine stray at large', 'Canine relinquished by owner', 
                'Canine intake owner intended euthanasia', 'Canine transferred in from agency', 
                'Canine other intakes', 'Canine Total Intake Gross']

    cat_columns = ['Feline stray at large', 'Feline relinquished by owner', 
                'Feline intake owner intended euthanasia', 'Feline transferred in from agency', 
                'Feline other intakes', 'Feline Total Intake Gross']

    # Group by state and sum the columns for dogs and cats
    dog_totals = df_filtered.groupby('State')[dog_columns].sum().sum(axis=1).sort_values(ascending=False)
    cat_totals = df_filtered.groupby('State')[cat_columns].sum().sum(axis=1).sort_values(ascending=False)

    # Create bar plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 20))

    # Plot for dogs
    dog_totals.plot(kind='bar', ax=ax1)
    ax1.set_title('Total Stray Dogs by State (2021-2023)')
    ax1.set_xlabel('State')
    ax1.set_ylabel('Total Count')
    ax1.tick_params(axis='x', rotation=90)

    # Plot for cats
    cat_totals.plot(kind='bar', ax=ax2)
    ax2.set_title('Total Stray Cats by State (2021-2023)')
    ax2.set_xlabel('State')
    ax2.set_ylabel('Total Count')
    ax2.tick_params(axis='x', rotation=90)

    plt.tight_layout()
    plt.savefig('Total_Intake_Gross_BY_Species.png')

    ### Examining Net Intakes by State Segregated by Dog and Cat Animal Type

    # Remove Duplicate Entries
    df_filtered = df_filtered[df_filtered['Shelter Name Annotation'] != 'R']

    # Define column names for dogs and cats
    dog_columns = ['Canine stray at large', 'Canine relinquished by owner', 
                'Canine intake owner intended euthanasia', 'Canine Total Intake Net']

    cat_columns = ['Feline stray at large', 'Feline relinquished by owner', 
                'Feline intake owner intended euthanasia', 'Feline Total Intake Net']

    # Group by state and sum the columns for dogs and cats
    dog_totals = df_filtered.groupby('State')[dog_columns].sum().sum(axis=1).sort_values(ascending=False)
    cat_totals = df_filtered.groupby('State')[cat_columns].sum().sum(axis=1).sort_values(ascending=False)

    # Create bar plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 20))

    # Plot for dogs
    dog_totals.plot(kind='bar', ax=ax1)
    ax1.set_title('Total Stray Dogs by State (2021-2023)')
    ax1.set_xlabel('State')
    ax1.set_ylabel('Total Count')
    ax1.tick_params(axis='x', rotation=90)

    # Plot for cats
    cat_totals.plot(kind='bar', ax=ax2)
    ax2.set_title('Total Stray Cats by State (2021-2023)')
    ax2.set_xlabel('State')
    ax2.set_ylabel('Total Count')
    ax2.tick_params(axis='x', rotation=90)

    plt.tight_layout()
    plt.savefig('Total_Intake_Net.png')

    ### Top 10 Shelters by Animal Count 

    shelter_filtered = combined_df[pd.to_numeric(combined_df['Data Year'], errors='coerce').between(2021, 2023)]

    # Filter out rows where 'Data Year' is NaN (which includes the string values)
    shelter_filtered = combined_df.dropna(subset=['Data Year'])

    # Filter for years 2021-2023
    shelter_filtered = shelter_filtered[shelter_filtered['Data Year'].isin([2021, 2022, 2023])]

    # Remove Duplicate Entries

    shelter_filtered = shelter_filtered[shelter_filtered['Shelter Name Annotation'] != 'R']

    # Define all relevant columns
    animal_columns = ['Canine stray at large', 'Canine relinquished by owner', 
                    'Canine intake owner intended euthanasia', 'Canine transferred in from agency', 
                    'Canine other intakes', 'Canine Total Intake Gross',
                    'Feline stray at large', 'Feline relinquished by owner', 
                    'Feline intake owner intended euthanasia', 'Feline transferred in from agency', 
                    'Feline other intakes', 'Feline Total Intake Gross']

    # Calculate total animal count for each shelter and year
    shelter_filtered['Total Animals'] = shelter_filtered[animal_columns].sum(axis=1)

    # Group by Shelter Name and Data Year, summing the total animals
    grouped = shelter_filtered.groupby(['Shelter Name', 'Data Year'])['Total Animals'].sum().unstack()

    # Calculate the total animals for each shelter across all years
    shelter_totals = grouped.sum(axis=1)

    # Get the top 10 shelters
    top_10_shelters = shelter_totals.nlargest(10).index

    # Filter the grouped data for only the top 10 shelters
    top_10_data = grouped.loc[top_10_shelters]

    # Create the time series plot
    plt.figure(figsize=(15, 10))

    for shelter in top_10_shelters:
        plt.plot(top_10_data.columns, top_10_data.loc[shelter], marker='o', label=shelter)

    plt.title('Top 10 Animal Shelters by Animal Count (2021-2023)')
    plt.xlabel('Year')
    plt.ylabel('Total Animal Count')
    plt.legend(title='Shelter Name', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('Top_10_Shelters.png')

    ### Top 10 Shelters by Animal Count Separated by Year

    # Convert 'Data Year' to numeric, coercing errors to NaN
    combined_df['Data Year'] = pd.to_numeric(combined_df['Data Year'], errors='coerce')

    # Filter out rows where 'Data Year' is NaN (which includes the string values)
    shelter_filtered_year = combined_df.dropna(subset=['Data Year'])

    # Filter for years 2021-2023
    shelter_filtered_year = shelter_filtered_year[shelter_filtered_year['Data Year'].isin([2021, 2022, 2023])]

    # Define all relevant columns
    animal_columns = ['Canine stray at large', 'Canine relinquished by owner', 
                    'Canine intake owner intended euthanasia', 'Canine transferred in from agency', 
                    'Canine other intakes', 'Canine Total Intake Gross',
                    'Feline stray at large', 'Feline relinquished by owner', 
                    'Feline intake owner intended euthanasia', 'Feline transferred in from agency', 
                    'Feline other intakes', 'Feline Total Intake Gross']

    # Remove Duplicate Entries
    shelter_filtered_year = shelter_filtered_year[shelter_filtered_year['Shelter Name Annotation'] != 'R']

    # Calculate total animal count for each shelter and year
    shelter_filtered_year['Total Animals'] = shelter_filtered_year[animal_columns].sum(axis=1)

    # Group by Shelter Name and Data Year, summing the total animals
    grouped = shelter_filtered_year.groupby(['Shelter Name', 'Data Year'])['Total Animals'].sum().unstack()

    # Calculate the total animals for each shelter across all years
    shelter_totals = grouped.sum(axis=1)

    # Get the top 10 shelters
    top_10_shelters = shelter_totals.nlargest(10).index

    # Filter the grouped data for only the top 10 shelters
    top_10_data = grouped.loc[top_10_shelters]

    # Melt the dataframe for easier plotting
    melted_data = top_10_data.reset_index().melt(id_vars='Shelter Name', var_name='Year', value_name='Total Animals')

    # Create the vertical bar plot
    plt.figure(figsize=(15, 10))
    sns.barplot(x='Shelter Name', y='Total Animals', hue='Year', data=melted_data)

    plt.title('Top 10 Animal Shelters by Animal Count (2021-2023)', fontsize=16)
    plt.xlabel('Shelter Name', fontsize=12)
    plt.ylabel('Total Animal Count', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Year')

    # Add value labels on top of each bar
    for i in plt.gca().containers:
        plt.gca().bar_label(i, label_type='edge', fontsize=8, padding=2)

    plt.tight_layout()
    plt.savefig('Total_10_Shelters_By_Count.png')

    ### Understanding Health Outcomes in the State of Georgia

    # Define the outcome columns for both canines and felines
    outcome_columns = [
        'Canine adoption', 'Feline adoption', 
        'Canine returned to owner', 'Feline returned to owner', 
        'Canine transferred to another agency', 'Feline transferred to another agency', 
        'Canine returned to field', 'Feline returned to field', 
        'Canine other live outcome', 'Feline other live outcome', 
        'Canine died in care', 'Feline died in care', 
        'Canine lost in care', 'Feline list in care', 
        'Canine shelter euthanasia', 'Feline shelter euthanasia', 
        'Canine owner intended euthanasia', 'Feline owner intended euthanasia'
    ]

    # Subset the DataFrame into canine and feline outcomes
    canine_df = combined_df[[col for col in outcome_columns if 'Canine' in col]]
    feline_df  = combined_df[[col for col in outcome_columns if 'Feline' in col]]

    # Calculate the total number of outcomes for canines and felines
    canine_totals = canine_df.sum()
    feline_totals = feline_df.sum()

    # Create a DataFrame for the counts
    canine_outcomes = pd.DataFrame({'outcome_type': canine_totals.index, 'count': canine_totals.values})
    feline_outcomes = pd.DataFrame({'outcome_type': feline_totals.index, 'count': feline_totals.values})

    canine_outcomes

    # Generate the Canine bar plot
    plt.figure(figsize=(10, 6))
    plt.barh(canine_outcomes['outcome_type'], canine_outcomes['count'], color='skyblue')
    plt.title('Canine Outcomes in Shelter System')
    plt.xlabel('Count')
    plt.ylabel('Outcome Type')
    plt.grid(axis='x')
    plt.tight_layout()
    plt.savefig('Canine_Outcomes.png')

    # Generate the Feline bar plot
    plt.figure(figsize=(10, 6))
    plt.barh(feline_outcomes['outcome_type'], feline_outcomes['count'], color='skyblue')
    plt.title('Feline Outcomes in Shelter System')
    plt.xlabel('Count')
    plt.ylabel('Outcome Type')
    plt.grid(axis='x')
    plt.tight_layout()
    plt.savefig('Feline_Outcomes.png')

    ### Examining Undesignated Species Total Intakes by State

    # Filter the data for years 2021-2023
    df_filtered_undesignated = combined_df[pd.to_numeric(combined_df['Data Year'], errors='coerce').between(2021, 2023)]

    # Group by State and sum the relevant columns
    columns_to_sum = [ 'Undesignated Species Total Intake Gross']

    state_totals = df_filtered_undesignated.groupby('State')[columns_to_sum].sum().sum(axis=1).sort_values(ascending=False)

    # Create the bar plot
    plt.figure(figsize=(35, 30))
    state_totals.plot(kind='bar')

    # Customize the plot
    plt.title('Total Undesignated Stray Pets by State (2021-2023)', fontsize=16)
    plt.xlabel('State', fontsize=12)
    plt.ylabel('Total Count', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Add value labels on top of each bar
    for i, v in enumerate(state_totals):
        plt.text(i, v, f'{v:,.0f}', ha='center', va='bottom')

    # Show the plot
    plt.savefig('Total_Intake_Gross_Undesignated.png')

    print("Dataset transformation script successfully completed.")

if __name__=='__main__':

    main()


