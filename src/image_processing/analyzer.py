"""
Image analyzer module using OpenAI's vision capabilities
"""

import os
import base64
from PIL import Image
import io
import colorsys
import openai
from pydantic import BaseModel
from typing import List, Optional

class ImageMetadata(BaseModel):
    """Image metadata model"""
    original_filename: str
    short_description: str
    categories: List[str]
    is_color: bool  # True if color, False if black and white
    mood: Optional[str] = None

class ImageAnalyzer:
    """
    Analyzes images using OpenAI's Vision capabilities
    """
    
    def __init__(self, custom_categories=None, custom_moods=None):
        """
        Initialize the image analyzer
        
        Args:
            custom_categories (list, optional): Custom categories to use for image classification
            custom_moods (list, optional): Custom mood options to use for image classification
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = api_key
        
        # Set default categories if none provided
        self.categories = custom_categories or [
            "nature", "people", "urban", "food", "animals", 
            "abstract", "landscape", "architecture", "product", "art", "technology"
        ]
        
        # Set default moods if none provided
        self.moods = custom_moods or [
            "happy", "sad", "calm", "energetic", "peaceful", 
            "tense", "mysterious", "romantic", "nostalgic", "dramatic"
        ]
        
    def _encode_image_to_base64(self, image_path):
        """
        Encode an image to base64
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            str: Base64-encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _is_color_image(self, image_path):
        """
        Determine if an image is color or black and white
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            bool: True if the image is in color, False if black and white
        """
        # Open image and convert to RGB
        img = Image.open(image_path).convert('RGB')
        
        # Resize for faster processing
        img = img.resize((100, 100))
        
        # Get colors
        colors = img.getcolors(10000)  # Get all colors
        
        # Check if the image has meaningful color variation
        is_color = False
        for _, (r, g, b) in colors:
            # TODO: is this true
            # If R, G, and B values differ by more than a threshold, it's a color image
            if max(abs(r - g), abs(r - b), abs(g - b)) > 15:
                is_color = True
                break
                
        return is_color
    
    def analyze(self, image_path, original_filename):
        """
        Analyze an image using OpenAI's Vision capabilities
        
        Args:
            image_path (str): Path to the image
            original_filename (str): Original filename
            
        Returns:
            ImageMetadata: Extracted metadata
        """
        # Encode image to base64
        base64_image = self._encode_image_to_base64(image_path)
        
        # Check if image is color or black and white
        is_color = self._is_color_image(image_path)
        
        # Format categories and moods for the prompt
        categories_str = ", ".join(self.categories)
        moods_str = ", ".join(self.moods)
        
        # Construct the prompt
        prompt = f"""
        Analyze this image and provide the following information:
        1. A concise description (5 words or less) that captures the essence of the image
        2. Categories that apply to this image (comma-separated, choose from: {categories_str})
        3. The overall mood/feeling of the image (choose one from: {moods_str})
        
        Format your response as:
        Short Description: [short description]
        Categories: [category1, category2, ...]
        Mood: [mood]
        """
        
        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Use the current stable model that supports vision
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        # Parse the response
        result = response.choices[0].message['content']
        
        # Extract information
        short_description = ""
        categories = []
        mood = ""
        
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith("Short Description:"):
                short_description = line.replace("Short Description:", "").strip().upper()
            elif line.startswith("Categories:"):
                categories_str = line.replace("Categories:", "").strip()
                categories = [cat.strip() for cat in categories_str.split(',')]
            elif line.startswith("Mood:"):
                mood = line.replace("Mood:", "").strip()
        
        # Create and return the metadata
        return ImageMetadata(
            original_filename=original_filename,
            short_description=short_description,
            categories=categories,
            is_color=is_color,
            mood=mood
        ) 