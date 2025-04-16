"""
Import module for categories and moods from CSV or TXT files
"""

import os
import csv
import tempfile

def import_from_file(file_path):
    """
    Import categories and moods from a CSV or TXT file
    
    The expected file format is:
    - For CSV: Two columns, first for categories, second for moods
    - For TXT: Two sections, one for categories and one for moods, 
               separated by a line containing only "---"
    
    Args:
        file_path (str): Path to the import file
        
    Returns:
        tuple: (categories, moods) lists
    """
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.csv':
        return _import_from_csv(file_path)
    elif file_extension.lower() == '.txt':
        return _import_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Please use .csv or .txt files.")

def _import_from_csv(file_path):
    """
    Import from a CSV file
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        tuple: (categories, moods) lists
    """
    categories = []
    moods = []
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 1 and row[0].strip():
                categories.append(row[0].strip())
            if len(row) >= 2 and row[1].strip():
                moods.append(row[1].strip())
    
    return categories, moods

def _import_from_txt(file_path):
    """
    Import from a TXT file
    
    The file should have categories listed first, then a separator line with only "---",
    then the moods list.
    
    Args:
        file_path (str): Path to the TXT file
        
    Returns:
        tuple: (categories, moods) lists
    """
    categories = []
    moods = []
    
    current_section = 'categories'  # Start with categories section
    
    with open(file_path, 'r', encoding='utf-8') as txtfile:
        for line in txtfile:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
                
            if line == '---':
                current_section = 'moods'  # Switch to moods section
                continue
                
            if current_section == 'categories':
                categories.append(line)
            else:
                moods.append(line)
    
    return categories, moods

def save_temp_file(file_content):
    """
    Save uploaded file content to a temporary file
    
    Args:
        file_content (bytes): The binary content of the uploaded file
        
    Returns:
        str: Path to the temporary file
    """
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp()
    
    try:
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(file_content)
    except:
        os.remove(temp_path)
        raise
        
    return temp_path 