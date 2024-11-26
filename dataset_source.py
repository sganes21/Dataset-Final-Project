import pandas as pd

def load_data(url):
    """
    Loads data from the provided URL and returns a pandas DataFrame.

    Parameters:
        url (str): The URL of the Excel file to load.

    Returns:
        pd.DataFrame: The loaded DataFrame.
    """
    try:
        # Read the Excel file from the URL
        df = pd.read_excel(url)
        print("Data successfully loaded.")
        return df
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        return None