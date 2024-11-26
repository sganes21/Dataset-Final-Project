import pytest
import pandas as pd
import numpy as np
from dataset_transformation import get_detailed_dtypes  # Replace 'your_module' with the actual module name

def test_get_detailed_dtypes():
    # Create a sample DataFrame
    df = pd.DataFrame({
        'A': [1, 2, 3, np.nan],
        'B': ['a', 'b', 'c', 'd'],
        'C': [1.1, 2.2, 3.3, 4.4],
        'D': [True, False, True, False]
    })

    # Call the function
    result = get_detailed_dtypes(df)

    # Assert the structure of the result
    assert isinstance(result, dict)
    assert set(result.keys()) == set(df.columns)

    # Check details for column 'A'
    assert result['A']['pandas_dtype'] == 'float64'
    assert result['A']['python_types'] == {float: 4}
    assert result['A']['nan_count'] == 1
    assert result['A']['unique_values'] == 3

    # Check details for column 'B'
    assert result['B']['pandas_dtype'] == 'object'
    assert result['B']['python_types'] == {str: 4}
    assert result['B']['nan_count'] == 0
    assert result['B']['unique_values'] == 4

    # Check details for column 'C'
    assert result['C']['pandas_dtype'] == 'float64'
    assert result['C']['python_types'] == {float: 4}
    assert result['C']['nan_count'] == 0
    assert result['C']['unique_values'] == 4

    # Check details for column 'D'
    assert result['D']['pandas_dtype'] == 'bool'
    assert result['D']['python_types'] == {bool: 4}
    assert result['D']['nan_count'] == 0
    assert result['D']['unique_values'] == 2