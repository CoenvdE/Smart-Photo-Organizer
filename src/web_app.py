#!/usr/bin/env python3
"""
Smart Photo Organizer Web App
Streamlit-based web interface
"""

import os
import sys
import tempfile
import shutil
import zipfile
import pandas as pd
import streamlit as st
from pathlib import Path

# Import local modules
from auth.google_auth import authenticate
from drive.connector import DriveConnector
from drive.utils import select_folder, create_output_folder
from image_processing.analyzer import ImageAnalyzer
from image_processing.renamer import rename_images
from metadata.export import export_metadata
from metadata.import_file import import_from_file, save_temp_file

# Set page config
st.set_page_config(
    page_title="Smart Photo Organizer",
    page_icon="📷",
    layout="wide",
)

# Configure OpenAI API key


def configure_api_keys():
    """Configure API keys from Streamlit secrets or environment variables"""
    try:
        # Try to get API key from Streamlit secrets
        if 'OPENAI_API_KEY' in st.secrets:
            os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

        # Check if API key is set
        if 'OPENAI_API_KEY' not in os.environ:
            st.error(
                "OpenAI API key not found! "
                "Please set it in Streamlit secrets or as an environment variable."
            )

            # Provide option to enter API key manually
            api_key = st.text_input(
                "Enter your OpenAI API key:", type="password")
            if api_key:
                os.environ['OPENAI_API_KEY'] = api_key
                st.success("API key set successfully!")
                return True
            else:
                st.info("Please enter your OpenAI API key to continue.")
                return False
        return True
    except Exception as e:
        st.error(f"Error configuring API keys: {str(e)}")

        # Provide option to enter API key manually
        api_key = st.text_input("Enter your OpenAI API key:", type="password")
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            st.success("API key set successfully!")
            return True
        else:
            st.info("Please enter your OpenAI API key to continue.")
            return False


def main():
    """Main entry point for the Streamlit app"""

    st.title("Smart Photo Organizer")
    st.subheader("Organize your photos with AI")

    # Configure API keys
    if not configure_api_keys():
        # If API key configuration failed, don't proceed further
        return

    # Sidebar for app navigation and options
    with st.sidebar:
        st.header("Options")
        # Temporarily disable Google Drive option
        # source_option = st.radio(
        #     "Choose image source:",
        #     ["Upload Local Images", "Connect to Google Drive"]
        # )
        source_option = "Upload Local Images"
        st.info(
            "Google Drive integration is temporarily disabled. Only local uploads are available.")

        # Export format option
        export_format = st.selectbox(
            "Export format:",
            ["excel", "csv"],
            index=0
        )

        # Categories and moods options
        categories_option = st.radio(
            "Categories and moods:",
            ["Use defaults", "Import from file", "Enter manually"]
        )

        custom_categories = None
        custom_moods = None

        if categories_option == "Import from file":
            cat_mood_file = st.file_uploader(
                "Upload categories and moods file (CSV or TXT)",
                type=["csv", "txt"]
            )

            if cat_mood_file is not None:
                try:
                    # Save uploaded file to a temporary file
                    temp_path = save_temp_file(cat_mood_file.getvalue())

                    # Import categories and moods
                    custom_categories, custom_moods = import_from_file(
                        temp_path)

                    # Clean up
                    os.unlink(temp_path)

                    st.success(
                        f"Imported {len(custom_categories)} categories and {len(custom_moods)} moods.")

                    # Display imported categories and moods
                    with st.expander("View imported categories and moods"):
                        st.write("**Categories:**")
                        st.write(", ".join(custom_categories))
                        st.write("**Moods:**")
                        st.write(", ".join(custom_moods))

                except Exception as e:
                    st.error(f"Error importing file: {str(e)}")

        elif categories_option == "Enter manually":
            categories_input = st.text_area(
                "Enter categories (one per line):",
                height=100,
                help="Enter one category per line"
            )

            moods_input = st.text_area(
                "Enter moods (one per line):",
                height=100,
                help="Enter one mood per line"
            )

            if categories_input:
                custom_categories = [
                    c.strip() for c in categories_input.strip().split("\n") if c.strip()]

            if moods_input:
                custom_moods = [m.strip()
                                for m in moods_input.strip().split("\n") if m.strip()]

            if custom_categories or custom_moods:
                st.success(
                    f"Using {len(custom_categories or [])} custom categories and {len(custom_moods or [])} custom moods.")

    # Main content based on selected source
    if source_option == "Upload Local Images":
        process_local_images(export_format, custom_categories, custom_moods)
    else:
        process_drive_images(export_format, custom_categories, custom_moods)


def process_local_images(export_format, custom_categories, custom_moods):
    """Process locally uploaded images"""

    st.header("Upload Images")

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload images",
        type=["jpg", "jpeg", "png", "gif", "bmp"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("Please upload one or more image files to begin.")
        return

    # Create a button to process the images
    if st.button("Process Images"):
        with st.spinner("Processing images..."):
            # Create temp directory to store images
            temp_dir = tempfile.mkdtemp()
            output_dir = tempfile.mkdtemp()

            try:
                # Save uploaded images to temp directory
                image_paths = []
                for uploaded_file in uploaded_files:
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    image_paths.append(
                        {"path": temp_path, "name": uploaded_file.name})

                # Initialize image analyzer
                analyzer = ImageAnalyzer(
                    custom_categories=custom_categories,
                    custom_moods=custom_moods
                )

                # Process images
                processed_images = []

                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, image in enumerate(image_paths):
                    status_text.text(f"Processing {image['name']}...")

                    # Analyze image
                    metadata = analyzer.analyze(image['path'], image['name'])

                    # Add to processed list
                    processed_images.append({
                        'original_file': {'name': image['name']},
                        'temp_path': image['path'],
                        'metadata': metadata
                    })

                    # Update progress
                    progress_bar.progress((i + 1) / len(image_paths))

                # Rename images based on metadata
                status_text.text("Renaming images...")
                renamed_images = rename_images(processed_images)

                # Copy renamed images to output directory
                for image in renamed_images:
                    output_path = os.path.join(output_dir, image['new_name'])
                    shutil.copy2(image['temp_path'], output_path)

                # Export metadata
                status_text.text("Exporting metadata...")
                metadata_file = export_metadata(renamed_images, export_format)

                # Copy metadata file to output directory
                shutil.copy2(metadata_file, output_dir)

                # Create a zip file with all the processed files
                zip_path = os.path.join(temp_dir, "processed_images.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(output_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, output_dir)
                            zipf.write(file_path, arcname)

                # Clean up temporary metadata file
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)

                # Offer the zip file for download
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="Download Processed Images",
                        data=f,
                        file_name="processed_images.zip",
                        mime="application/zip"
                    )

                # Display the results
                st.success(
                    f"Successfully processed {len(renamed_images)} images!")

                # Show a table of the processed images
                results_df = pd.DataFrame([
                    {
                        'Original Filename': image['original_filename'],
                        'New Filename': image['new_name'],
                        'Short Description': image['metadata'].short_description,
                        'Categories': ', '.join(image['metadata'].categories),
                        'Color Type': 'Color' if image['metadata'].is_color else 'Black & White',
                        'Mood': image['metadata'].mood
                    }
                    for image in renamed_images
                ])

                st.dataframe(results_df)

            except Exception as e:
                st.error(f"Error processing images: {str(e)}")

            finally:
                # Clean up
                try:
                    shutil.rmtree(temp_dir)
                    shutil.rmtree(output_dir)
                except:
                    pass


def process_drive_images(export_format, custom_categories, custom_moods):
    """Process images from Google Drive"""

    st.header("Connect to Google Drive")

    # In the cloud, we'll need to provide a way to upload credentials.json
    credentials_file = Path("drive_json/credentials.json")

    if not credentials_file.exists():
        st.warning(
            "Google Drive credentials not found. Please upload your credentials.json file:"
        )

        # Add upload field for credentials.json
        credentials_upload = st.file_uploader(
            "Upload your credentials.json file",
            type=["json"]
        )

        if credentials_upload is not None:
            # Make sure the directory exists
            os.makedirs("drive_json", exist_ok=True)

            # Save credentials
            with open(credentials_file, "wb") as f:
                f.write(credentials_upload.getbuffer())

            st.success("Credentials file uploaded successfully!")
            st.rerun()

    # Connect to Google Drive
    if st.button("Connect to Google Drive"):
        try:
            with st.spinner("Authenticating with Google Drive..."):
                # Authenticate with Google Drive
                credentials = authenticate()

                # Create Drive connector
                drive = DriveConnector(credentials)

                st.session_state.drive = drive
                st.success("Successfully connected to Google Drive!")
                st.rerun()  # Rerun the app to update the UI

        except Exception as e:
            st.error(f"Error connecting to Google Drive: {str(e)}")

    # If connected, show folder selection
    if hasattr(st.session_state, 'drive'):
        drive = st.session_state.drive

        st.subheader("Select Folder")

        # Get top-level folders
        try:
            folders = drive.list_folders()

            if not folders:
                st.warning("No folders found in your Google Drive.")
                return

            folder_names = [
                f"{folder['name']} ({folder['id']})" for folder in folders]
            selected_folder = st.selectbox(
                "Select a folder to process:", folder_names)

            # Get the folder ID from the selected folder
            folder_id = selected_folder.split("(")[-1].strip(")")

            # Output folder name
            output_folder_name = st.text_input(
                "Output folder name:", "Processed Photos")

            if st.button("Process Images"):
                with st.spinner("Processing images from Google Drive..."):
                    try:
                        # Create output folder
                        output_folder_id = create_output_folder(
                            drive, output_folder_name)

                        # List image files in the input folder
                        image_files = drive.list_image_files(folder_id)

                        if not image_files:
                            st.warning(
                                "No image files found in the selected folder.")
                            return

                        st.info(f"Found {len(image_files)} image files.")

                        # Initialize image analyzer
                        analyzer = ImageAnalyzer(
                            custom_categories=custom_categories,
                            custom_moods=custom_moods
                        )

                        # Process images
                        processed_images = []

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        for i, image in enumerate(image_files):
                            status_text.text(f"Processing {image['name']}...")

                            # Download image to temporary location
                            temp_path = drive.download_file(image['id'])

                            # Analyze image
                            metadata = analyzer.analyze(
                                temp_path, image['name'])

                            # Add to processed list
                            processed_images.append({
                                'original_file': image,
                                'temp_path': temp_path,
                                'metadata': metadata
                            })

                            # Update progress
                            progress_bar.progress((i + 1) / len(image_files))

                        # Rename images based on metadata
                        status_text.text("Renaming images...")
                        renamed_images = rename_images(processed_images)

                        # Upload renamed images to output folder
                        status_text.text("Uploading renamed images...")
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
                        status_text.text("Exporting metadata...")
                        metadata_file = export_metadata(
                            renamed_images, export_format)

                        # Upload metadata file to output folder
                        drive.upload_file(
                            metadata_file,
                            os.path.basename(metadata_file),
                            output_folder_id
                        )

                        # Clean up metadata file
                        if os.path.exists(metadata_file):
                            os.remove(metadata_file)

                        st.success(
                            f"Successfully processed {len(renamed_images)} images!")
                        st.info(
                            f"Processed images and metadata saved to '{output_folder_name}' folder in Google Drive")

                        # Show a table of the processed images
                        results_df = pd.DataFrame([
                            {
                                'Original Filename': image['original_filename'],
                                'New Filename': image['new_name'],
                                'Short Description': image['metadata'].short_description,
                                'Categories': ', '.join(image['metadata'].categories),
                                'Color Type': 'Color' if image['metadata'].is_color else 'Black & White',
                                'Mood': image['metadata'].mood
                            }
                            for image in renamed_images
                        ])

                        st.dataframe(results_df)

                    except Exception as e:
                        st.error(f"Error processing images: {str(e)}")

        except Exception as e:
            st.error(f"Error listing folders: {str(e)}")


if __name__ == "__main__":
    main()
