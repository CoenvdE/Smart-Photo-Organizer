"""
Image renaming module
"""

import os
import re

def sanitize_description(description):
    """
    Sanitize a description for use in a filename
    
    Args:
        description (str): Description to sanitize
        
    Returns:
        str: Sanitized description
    """
    # Remove any characters that are not letters, numbers, or spaces
    sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', description)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Limit to 30 characters
    sanitized = sanitized[:30]
    
    # Ensure uppercase
    sanitized = sanitized.upper()
    
    return sanitized

def rename_images(processed_images):
    """
    Rename images based on their metadata
    
    Args:
        processed_images (list): List of processed image dictionaries
        
    Returns:
        list: List of dictionaries with renamed image information
    """
    renamed_images = []
    
    for i, image in enumerate(processed_images, 1):
        # Extract original filename and metadata
        original_filename = image['original_file']['name']
        metadata = image['metadata']
        
        # Get file extension
        _, extension = os.path.splitext(original_filename)
        
        # Sanitize the description
        description = sanitize_description(metadata.short_description)
        
        # Create the new filename
        new_name = f"{i:03d}-{description}{extension}"
        
        # Add to renamed images list
        renamed_images.append({
            'original_file': image['original_file'],
            'original_filename': original_filename,
            'temp_path': image['temp_path'],
            'new_name': new_name,
            'metadata': metadata
        })
    
    return renamed_images 