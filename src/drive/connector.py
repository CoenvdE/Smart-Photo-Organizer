"""
Google Drive connector for interacting with Drive API
"""

import os
import tempfile
import mimetypes
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

class DriveConnector:
    """
    Connector for Google Drive operations
    """
    
    def __init__(self, credentials):
        """
        Initialize the Drive connector
        
        Args:
            credentials: Google API credentials
        """
        self.service = build('drive', 'v3', credentials=credentials)
    
    def list_folders(self):
        """
        List all folders in the user's Drive
        
        Returns:
            list: List of folder dictionaries with 'id' and 'name' keys
        """
        results = self.service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id, name)"
        ).execute()
        
        return results.get('files', [])
    
    def list_image_files(self, folder_id):
        """
        List all image files in a specific folder
        
        Args:
            folder_id (str): Google Drive folder ID
            
        Returns:
            list: List of file dictionaries with 'id' and 'name' keys
        """
        # Define image mimetypes to search for
        image_mimetypes = [
            "image/jpeg", 
            "image/png", 
            "image/gif", 
            "image/tiff", 
            "image/bmp",
            "image/webp"
        ]
        
        # Build the mimetype query
        mimetype_query = " or ".join([f"mimeType='{mime}'" for mime in image_mimetypes])
        
        # Build the complete query
        query = f"(({mimetype_query})) and '{folder_id}' in parents and trashed=false"
        
        # Execute the query
        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType)"
        ).execute()
        
        return results.get('files', [])
    
    def download_file(self, file_id):
        """
        Download a file from Google Drive
        
        Args:
            file_id (str): Google Drive file ID
            
        Returns:
            str: Path to downloaded file
        """
        # Get file metadata
        file_metadata = self.service.files().get(fileId=file_id, fields="name").execute()
        file_name = file_metadata.get("name")
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1])
        temp_path = temp_file.name
        temp_file.close()
        
        # Download the file to the temporary path
        request = self.service.files().get_media(fileId=file_id)
        with open(temp_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        
        return temp_path
    
    def create_folder(self, name, parent_id=None):
        """
        Create a new folder in Google Drive
        
        Args:
            name (str): Folder name
            parent_id (str, optional): Parent folder ID
            
        Returns:
            str: New folder ID
        """
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        # Set parent if provided
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        # Create the folder
        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        return folder.get('id')
    
    def upload_file(self, file_path, file_name, parent_id=None):
        """
        Upload a file to Google Drive
        
        Args:
            file_path (str): Path to the file
            file_name (str): Name to use for the uploaded file
            parent_id (str, optional): Parent folder ID
            
        Returns:
            str: Uploaded file ID
        """
        # Guess the MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # Prepare file metadata
        file_metadata = {'name': file_name}
        
        # Set parent if provided
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        # Upload the file
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id') 