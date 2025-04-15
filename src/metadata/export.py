"""
Metadata export module
"""

import os
import tempfile
import pandas as pd
import shutil

def export_metadata(renamed_images, format='excel'):
    """
    Export image metadata to a file
    
    Args:
        renamed_images (list): List of renamed image dictionaries
        format (str): Export format ('excel' or 'csv')
        
    Returns:
        str: Path to the exported file
    """
    # Create a temporary file with appropriate suffix
    file_suffix = '.xlsx' if format == 'excel' else '.csv'
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
        temp_path = temp_file.name
    
    # Prepare data for DataFrame
    data = []
    for image in renamed_images:
        metadata = image['metadata']
        
        # Add to data list
        data.append({
            'Original Filename': image['original_filename'],
            'New Filename': image['new_name'],
            'Short Description': metadata.short_description,
            'Categories': ', '.join(metadata.categories),
            'Color Type': 'Color' if metadata.is_color else 'Black & White',
            'Mood': metadata.mood
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Export to file
    if format == 'excel':
        df.to_excel(temp_path, index=False, engine='openpyxl')
        
        # Adjust column widths for better readability
        with pd.ExcelWriter(temp_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Get the worksheet
            worksheet = writer.sheets['Sheet1']
            
            # Set column widths
            for i, col in enumerate(df.columns):
                # Find the maximum length of data in this column
                max_len = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2  # Add some extra space
                
                # Set the column width
                worksheet.column_dimensions[chr(65 + i)].width = max_len
    else:
        df.to_csv(temp_path, index=False)
    
    # Create the final file path with the desired filename
    final_filename = 'overview' + file_suffix
    final_path = os.path.join(os.path.dirname(temp_path), final_filename)
    
    # Copy the temp file to the final file with the desired name
    shutil.copy2(temp_path, final_path)
    
    # Clean up the temp file
    os.remove(temp_path)
    
    return final_path 