#!/usr/bin/env python3
"""
Smart Photo Organizer for Editors
Main entry point for the application
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Import local modules
from auth.google_auth import authenticate
from drive.connector import DriveConnector
from drive.utils import select_folder, create_output_folder
from image_processing.analyzer import ImageAnalyzer
from image_processing.renamer import rename_images
from metadata.export import export_metadata

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Smart Photo Organizer')
    parser.add_argument('--input-folder-id', help='Google Drive folder ID to process')
    parser.add_argument('--output-folder-name', default='Processed Photos', 
                        help='Name for the output folder')
    parser.add_argument('--format', choices=['csv', 'excel'], default='excel',
                        help='Format for metadata export (default: excel)')
    return parser.parse_args()

def main():
    """Main entry point for the application"""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Authenticate with Google Drive
        print("Authenticating with Google Drive...")
        credentials = authenticate()
        
        # Create Drive connector
        drive = DriveConnector(credentials)
        
        # Select input folder if not provided
        input_folder_id = args.input_folder_id
        if not input_folder_id:
            input_folder_id = select_folder(drive)
            if not input_folder_id:
                print("No folder selected. Exiting.")
                return 1
        
        # Create output folder
        output_folder_id = create_output_folder(drive, args.output_folder_name)
        
        # List image files in the input folder
        print(f"Listing image files in the selected folder...")
        image_files = drive.list_image_files(input_folder_id)
        
        if not image_files:
            print("No image files found in the selected folder.")
            return 1
        
        print(f"Found {len(image_files)} image files.")
        
        # Initialize image analyzer
        analyzer = ImageAnalyzer()
        
        # Process images
        print("Processing images...")
        processed_images = []
        
        for image in image_files:
            print(f"Processing {image['name']}...")
            # Download image to temporary location
            temp_path = drive.download_file(image['id'])
            
            # Analyze image
            metadata = analyzer.analyze(temp_path, image['name'])
            
            # Add to processed list
            processed_images.append({
                'original_file': image,
                'temp_path': temp_path,
                'metadata': metadata
            })
        
        # Rename images based on metadata
        print("Renaming images...")
        renamed_images = rename_images(processed_images)
        
        # Upload renamed images to output folder
        print("Uploading renamed images...")
        for image in renamed_images:
            drive.upload_file(
                image['temp_path'], 
                image['new_name'], 
                output_folder_id
            )
            
            # Clean up temporary file
            if os.path.exists(image['temp_path']):
                os.remove(image['temp_path'])
        
        # Export metadata
        print("Exporting metadata...")
        metadata_file = export_metadata(renamed_images, args.format)
        
        # Upload metadata file to output folder
        print("Uploading metadata file...")
        drive.upload_file(
            metadata_file,
            os.path.basename(metadata_file),
            output_folder_id
        )
        
        # Clean up metadata file
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
        
        print("Processing complete!")
        print(f"Processed images and metadata saved to '{args.output_folder_name}' folder in Google Drive")
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 