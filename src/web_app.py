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
import io
import imghdr
import mimetypes
from io import BytesIO

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

# Constants for security limits
MAX_ZIP_SIZE_MB = 200  # Maximum zip file size in MB
MAX_IMAGE_SIZE_MB = 50  # Maximum individual image size in MB
MAX_IMAGES_FROM_ZIP = 100  # Maximum number of images to extract from a zip
MAX_INDIVIDUAL_UPLOADS = 50  # Maximum number of individual files to upload

# File validation constants
VALID_IMAGE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'bmp']
VALID_IMAGE_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp']


def validate_image_file(file_path):
    """Validate that a file is actually an image by checking content"""
    try:
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            return False, f"File exceeds maximum size of {MAX_IMAGE_SIZE_MB}MB"

        # Check using imghdr to detect image type from content
        img_type = imghdr.what(file_path)
        if img_type is None or img_type.lower() not in VALID_IMAGE_TYPES:
            return False, "File does not appear to be a valid image"

        # Additional check with mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None or mime_type not in VALID_IMAGE_MIME_TYPES:
            return False, "File mime type is not recognized as an image"

        return True, "Valid image"
    except Exception as e:
        return False, f"Error validating image: {str(e)}"

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

    # App description and features
    with st.expander("ℹ️ About this app", expanded=False):
        st.markdown("""
        **Smart Photo Organizer** is an AI-powered tool that analyzes your photos and helps you organize them intelligently.
        
        ### What this app does:
        
        1. **Analysis** - Uses AI to analyze your photos and extract:
           - Short descriptive text
           - Categories (landscape, portrait, food, architecture, etc.)
           - Mood (calm, energetic, happy, etc.)
           - Color detection (color vs. black & white)
        
        2. **Smart Renaming** - Renames your files following the format: `0001-SHORT_DESCRIPTION.jpg`
        
        3. **Metadata Export** - Creates an Excel/CSV file containing all the extracted information
        
        4. **Organized Download** - Packages all renamed files and metadata into a convenient ZIP file
        
        ### Privacy Note:
        Images are analyzed using OpenAI's services (ChatGPT/GPT-4), so image data is sent to OpenAI for processing.
        Images are temporarily stored on this server during processing and then deleted.
        No data is permanently stored on our servers, but please be aware of OpenAI's privacy policy regarding uploaded content.
        """)

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
        st.subheader("Export Settings")
        export_format = st.selectbox(
            "Metadata export format:",
            ["excel", "csv"],
            index=0,
            help="Excel format includes formatting and is easier to read. CSV is more compatible with other software."
        )

        # Categories and moods options
        st.subheader("Customization")
        categories_option = st.radio(
            "Categories and moods:",
            ["Use defaults", "Import from file", "Enter manually"],
            help="You can customize the categories and moods used to organize your photos"
        )

        custom_categories = None
        custom_moods = None

        if categories_option == "Import from file":
            st.markdown("""
            **File format options:**
            - CSV: First column = Categories, Second column = Moods
            - TXT: Categories listed first, then '---' separator line, then Moods
            """)

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
            st.markdown("Enter one item per line in each text area.")

            categories_input = st.text_area(
                "Categories:",
                height=100,
                help="Enter one category per line (e.g., landscape, portrait, food)"
            )

            moods_input = st.text_area(
                "Moods:",
                height=100,
                help="Enter one mood per line (e.g., happy, sad, calm)"
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

    st.header("Upload Your Photos")

    # About section
    st.markdown("""
    **How it works:**
    1. Upload your images using one of the methods below
    2. Click "Process Images" to analyze with AI
    3. Download the ZIP file containing:
       - Renamed images based on their content
       - Excel/CSV file with all photo metadata (categories, moods, colors)
    """)

    # Upload type selection
    upload_type = st.radio(
        "Select upload method:",
        ["Individual Images", "Zip Archive"]
    )

    image_paths = []
    temp_dir = tempfile.mkdtemp()
    invalid_files = []

    if upload_type == "Individual Images":
        # File uploader for individual images with size limit warning
        st.warning(
            f"Maximum file size: {MAX_IMAGE_SIZE_MB}MB per image, up to {MAX_INDIVIDUAL_UPLOADS} images")

        # File uploader for individual images
        uploaded_files = st.file_uploader(
            "Drag & drop your photos here or click to browse",
            type=["jpg", "jpeg", "png", "gif", "bmp"],
            accept_multiple_files=True,
            help="Select multiple files by holding CTRL/CMD while clicking, or by dragging a selection box over them"
        )

        if not uploaded_files:
            st.info("Please upload one or more image files to begin.")
            return

        # Check if too many files uploaded
        if len(uploaded_files) > MAX_INDIVIDUAL_UPLOADS:
            st.error(
                f"Too many files uploaded. Maximum is {MAX_INDIVIDUAL_UPLOADS}.")
            return

        # Save and validate uploaded images
        with st.spinner("Validating uploaded images..."):
            for uploaded_file in uploaded_files:
                # Check file size first
                file_size_mb = sys.getsizeof(
                    uploaded_file.getbuffer()) / (1024 * 1024)
                if file_size_mb > MAX_IMAGE_SIZE_MB:
                    invalid_files.append(
                        f"{uploaded_file.name} (exceeds {MAX_IMAGE_SIZE_MB}MB size limit)")
                    continue

                # Save to temp directory for validation
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Validate the file is actually an image
                is_valid, message = validate_image_file(temp_path)
                if is_valid:
                    image_paths.append(
                        {"path": temp_path, "name": uploaded_file.name})
                else:
                    invalid_files.append(f"{uploaded_file.name} ({message})")
                    os.remove(temp_path)  # Remove invalid file

    else:  # Zip Archive
        # Display size limits
        st.warning(
            f"Maximum zip file size: {MAX_ZIP_SIZE_MB}MB, extracting up to {MAX_IMAGES_FROM_ZIP} images")

        # File uploader for zip file
        uploaded_zip = st.file_uploader(
            "Upload a ZIP archive containing your photos",
            type=["zip"],
            help="The app will extract and process only valid image files (JPG, PNG, GIF, BMP), ignoring all other files"
        )

        if not uploaded_zip:
            st.info("Please upload a zip file containing images to begin.")
            return

        # Check zip file size
        zip_size_mb = sys.getsizeof(uploaded_zip.getbuffer()) / (1024 * 1024)
        if zip_size_mb > MAX_ZIP_SIZE_MB:
            st.error(f"Zip file exceeds maximum size of {MAX_ZIP_SIZE_MB}MB")
            return

        # Extract image files from zip
        try:
            with st.spinner("Extracting and validating images from zip file..."):
                # Create a temporary file for the zip
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                    temp_zip.write(uploaded_zip.getbuffer())
                    temp_zip_path = temp_zip.name

                extracted_count = 0
                skipped_count = 0

                # Process the zip file in streaming mode
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    # Get list of all files in the zip
                    file_list = zip_ref.namelist()

                    # Filter to keep only files with image extensions first
                    image_extensions = [
                        '.jpg', '.jpeg', '.png', '.gif', '.bmp']
                    potential_image_files = [f for f in file_list if any(
                        f.lower().endswith(ext) for ext in image_extensions)]

                    if not potential_image_files:
                        st.error("No image files found in the zip archive.")
                        os.remove(temp_zip_path)
                        return

                    # Check if zip contains too many potential image files
                    # We use *2 as buffer before full extraction
                    if len(potential_image_files) > MAX_IMAGES_FROM_ZIP * 2:
                        st.error(
                            f"Zip contains too many files. Maximum is {MAX_IMAGES_FROM_ZIP}.")
                        os.remove(temp_zip_path)
                        return

                    # Extract and validate each file
                    for img_file in potential_image_files:
                        # Skip if we've reached the limit
                        if extracted_count >= MAX_IMAGES_FROM_ZIP:
                            skipped_count += 1
                            continue

                        # Skip directories
                        if img_file.endswith('/'):
                            continue

                        filename = os.path.basename(img_file)
                        if not filename:  # Skip if empty filename
                            continue

                        try:
                            # Extract the file to temporary location
                            temp_path = os.path.join(temp_dir, filename)

                            # Get file info to check size before extraction
                            file_info = zip_ref.getinfo(img_file)
                            file_size_mb = file_info.file_size / (1024 * 1024)

                            # Skip if file is too large
                            if file_size_mb > MAX_IMAGE_SIZE_MB:
                                invalid_files.append(
                                    f"{filename} (exceeds {MAX_IMAGE_SIZE_MB}MB size limit)")
                                continue

                            # Check for zip path traversal vulnerability
                            if os.path.isabs(filename) or '..' in filename:
                                invalid_files.append(
                                    f"{img_file} (invalid path)")
                                continue

                            # Extract file safely
                            with zip_ref.open(img_file) as source, open(temp_path, 'wb') as target:
                                shutil.copyfileobj(source, target)

                            # Validate the file is actually an image
                            is_valid, message = validate_image_file(temp_path)
                            if is_valid:
                                image_paths.append(
                                    {"path": temp_path, "name": filename})
                                extracted_count += 1
                            else:
                                invalid_files.append(f"{filename} ({message})")
                                os.remove(temp_path)  # Remove invalid file

                        except Exception as e:
                            invalid_files.append(
                                f"{img_file} (error: {str(e)})")
                            # Clean up if needed
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

                # Clean up the temporary zip file
                os.remove(temp_zip_path)

                # Report results
                if extracted_count > 0:
                    st.success(
                        f"Extracted {extracted_count} valid image files from the zip archive.")
                    if skipped_count > 0:
                        st.warning(
                            f"Skipped {skipped_count} files due to limit of {MAX_IMAGES_FROM_ZIP} images.")
                else:
                    st.error("No valid image files found in the zip archive.")
                    return

        except zipfile.BadZipFile:
            st.error("The uploaded file is not a valid zip archive.")
            return
        except Exception as e:
            st.error(f"Error extracting zip file: {str(e)}")
            return

    # Display invalid files if any
    if invalid_files:
        with st.expander(f"⚠️ {len(invalid_files)} files were skipped", expanded=True):
            for invalid_file in invalid_files:
                st.warning(invalid_file)

    # Create a button to process the images
    if image_paths:
        st.info(f"Ready to process {len(image_paths)} images")

        # Show preview of what will happen
        with st.expander("What happens when you process the images?"):
            st.markdown("""
            When you click "Process Images":
            
            1. **AI Analysis**: Each image is analyzed to extract:
               - A short description of the image content
               - Relevant categories (e.g., landscape, portrait, food)
               - The overall mood of the image
               - Whether the image is color or black & white
               
            2. **Smart Renaming**: Files are renamed to a format like `0001-SUNSET_AT_BEACH.jpg`
            
            3. **Metadata Export**: All information is compiled into an Excel/CSV file
            
            4. **ZIP Package**: All processed files are packaged into a downloadable ZIP file
            """)

        process_button = st.button(
            "🔍 Process Images", type="primary", use_container_width=True)

        if process_button:
            if not image_paths:
                st.error("No valid images to process. Please upload images first.")
                return

            with st.spinner("Processing images..."):
                output_dir = tempfile.mkdtemp()

                try:
                    # Initialize image analyzer
                    analyzer = ImageAnalyzer(
                        custom_categories=custom_categories,
                        custom_moods=custom_moods
                    )

                    # Process images with improved error handling
                    processed_images = []
                    failed_images = []

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, image in enumerate(image_paths):
                        status_text.text(f"Processing {image['name']}...")
                        try:
                            # Analyze image
                            metadata = analyzer.analyze(
                                image['path'], image['name'])

                            # Add to processed list
                            processed_images.append({
                                'original_file': {'name': image['name']},
                                'temp_path': image['path'],
                                'metadata': metadata
                            })
                        except Exception as e:
                            failed_images.append(
                                f"{image['name']} (error: {str(e)})")
                            continue
                        finally:
                            # Update progress even if image fails
                            progress_bar.progress((i + 1) / len(image_paths))

                    # If no images were processed successfully
                    if not processed_images:
                        st.error(
                            "All images failed processing. Please try different images.")
                        # Display errors
                        if failed_images:
                            with st.expander("Processing errors", expanded=True):
                                for failed in failed_images:
                                    st.error(failed)
                        return

                    # Display any failed images
                    if failed_images:
                        with st.expander(f"{len(failed_images)} images failed processing", expanded=True):
                            for failed in failed_images:
                                st.error(failed)

                    # Rename images based on metadata
                    status_text.text("Renaming images...")
                    renamed_images = rename_images(processed_images)

                    # Copy renamed images to output directory
                    for image in renamed_images:
                        output_path = os.path.join(
                            output_dir, image['new_name'])
                        shutil.copy2(image['temp_path'], output_path)

                    # Export metadata
                    status_text.text("Exporting metadata...")
                    metadata_file = export_metadata(
                        renamed_images, export_format)

                    # Copy metadata file to output directory
                    shutil.copy2(metadata_file, output_dir)

                    # Create a zip file with all the processed files
                    zip_path = os.path.join(temp_dir, "processed_images.zip")
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for root, _, files in os.walk(output_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(
                                    file_path, output_dir)
                                zipf.write(file_path, arcname)

                    # Clean up temporary metadata file
                    if os.path.exists(metadata_file):
                        os.remove(metadata_file)

                    # Display the results
                    st.success(
                        f"Successfully processed {len(renamed_images)} images!")

                    # Provide download details
                    st.markdown("""
                    ### Your processed images are ready!
                    
                    The ZIP file contains:
                    - All your images renamed based on their content
                    - An Excel/CSV file with detailed metadata for each image
                    
                    You can use this metadata to:
                    - Sort images by category, mood, or color type
                    - Search for specific image content
                    - Group similar images together
                    """)

                    # Offer the zip file for download with a more prominent button
                    with open(zip_path, "rb") as f:
                        st.download_button(
                            label="📦 Download Processed Images and Metadata",
                            data=f,
                            file_name="processed_images.zip",
                            mime="application/zip",
                            use_container_width=True
                        )

                    # Show a table of the processed images with more context
                    st.subheader("Metadata Summary")
                    st.markdown(
                        "Below is a summary of the analysis for each processed image:")

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
