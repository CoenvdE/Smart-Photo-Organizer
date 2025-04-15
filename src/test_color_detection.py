#!/usr/bin/env python3
"""
Test script for color detection
"""

import os
import sys
import argparse
from PIL import Image

# Set up path to be able to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.image_processing.analyzer import ImageAnalyzer

def detect_color(image_path):
    """
    Test the color detection on a single image
    
    Args:
        image_path (str): Path to the image
    """
    # Initialize the analyzer
    analyzer = ImageAnalyzer()
    
    # Check if image is color or black and white
    is_color = analyzer._is_color_image(image_path)
    
    # Print result
    print(f"Image: {os.path.basename(image_path)}")
    print(f"Color type: {'Color' if is_color else 'Black & White'}")
    
    return is_color

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Test color detection')
    parser.add_argument('image_path', help='Path to the image file')
    args = parser.parse_args()
    
    if not os.path.isfile(args.image_path):
        print(f"Error: File not found: {args.image_path}")
        return 1
    
    # Detect if the image is color or black and white
    detect_color(args.image_path)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 