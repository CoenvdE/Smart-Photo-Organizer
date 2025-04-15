"""
Test imports to ensure project structure is correct
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestImports(unittest.TestCase):
    """Test that all modules can be imported correctly"""
    
    def test_auth_imports(self):
        """Test auth module imports"""
        from src.auth.google_auth import authenticate
        self.assertTrue(callable(authenticate))
    
    def test_drive_imports(self):
        """Test drive module imports"""
        from src.drive.connector import DriveConnector
        from src.drive.utils import select_folder, create_output_folder
        self.assertTrue(callable(DriveConnector))
        self.assertTrue(callable(select_folder))
        self.assertTrue(callable(create_output_folder))
    
    def test_image_processing_imports(self):
        """Test image processing module imports"""
        from src.image_processing.analyzer import ImageAnalyzer, ImageMetadata
        from src.image_processing.renamer import rename_images, sanitize_description
        self.assertTrue(callable(ImageAnalyzer))
        self.assertTrue(callable(rename_images))
        self.assertTrue(callable(sanitize_description))
    
    def test_metadata_imports(self):
        """Test metadata module imports"""
        from src.metadata.export import export_metadata
        self.assertTrue(callable(export_metadata))

if __name__ == "__main__":
    unittest.main() 