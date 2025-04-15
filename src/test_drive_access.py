#!/usr/bin/env python3
"""
Test script to check Google Drive access
"""

import sys
import os

# Set up path to be able to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from src.auth.google_auth import authenticate
    from src.drive.connector import DriveConnector
    
    print("Authenticating with Google Drive...")
    credentials = authenticate()
    
    print("Creating Drive connector...")
    drive = DriveConnector(credentials)
    
    print("\nListing folders in your Google Drive:")
    print("-" * 60)
    folders = drive.list_folders()
    
    if not folders:
        print("No folders found in your Google Drive.")
    else:
        for i, folder in enumerate(folders, 1):
            print(f"{i}. {folder['name']} (ID: {folder['id']})")
    
    print("\nListing recent image files:")
    print("-" * 60)
    # Get a sample of image files from any folder
    if folders and len(folders) > 0:
        # Try to get images from the first folder
        folder_id = folders[0]['id']
        images = drive.list_image_files(folder_id)
        
        if not images:
            print(f"No image files found in folder '{folders[0]['name']}'.")
        else:
            print(f"Found {len(images)} images in folder '{folders[0]['name']}':")
            for i, image in enumerate(images[:5], 1):  # Show only first 5 images
                print(f"{i}. {image['name']} (ID: {image['id']})")
            
            if len(images) > 5:
                print(f"... and {len(images) - 5} more images")
    
    print("\nGoogle Drive access test completed successfully.")
    
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1) 