"""
Image analyzer module using OpenAI's vision capabilities
"""

import os
import base64
from PIL import Image
import io
import colorsys
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional

class ImageMetadata(BaseModel):
    """Image metadata model"""
    original_filename: str
    short_description: str
    categories: List[str]
    dominant_colors: List[str]
    mood: Optional[str] = None

class ImageAnalyzer:
    """
    Analyzes images using OpenAI's Vision capabilities
    """
    
    def __init__(self):
        """Initialize the image analyzer"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        
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
    
    def _extract_dominant_colors(self, image_path, num_colors=5):
        """
        Extract dominant colors from an image
        
        Args:
            image_path (str): Path to the image
            num_colors (int): Number of dominant colors to extract
            
        Returns:
            list: List of color names
        """
        # Open image and convert to RGB
        img = Image.open(image_path).convert('RGB')
        
        # Resize for faster processing
        img = img.resize((100, 100))
        
        # Get colors
        colors = img.getcolors(10000)  # Get all colors
        
        # Sort by count (first element in the tuple)
        colors.sort(reverse=True, key=lambda x: x[0])
        
        # Take top num_colors
        top_colors = colors[:num_colors]
        
        # Convert RGB to color names (using simple RGB descriptors)
        color_names = []
        for count, (r, g, b) in top_colors:
            # Convert RGB to HSV for better color naming
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            
            # Determine color name based on HSV
            color_name = self._get_color_name(h, s, v)
            if color_name not in color_names:  # Avoid duplicates
                color_names.append(color_name)
        
        return color_names
    
    def _get_color_name(self, h, s, v):
        """
        Get a color name from HSV values
        
        Args:
            h (float): Hue [0,1]
            s (float): Saturation [0,1]
            v (float): Value [0,1]
            
        Returns:
            str: Color name
        """
        # Convert hue to degrees for easier comparison
        h_deg = h * 360
        
        # For grayscale colors
        if s < 0.1:
            if v < 0.3:
                return "Black"
            elif v < 0.7:
                return "Gray"
            else:
                return "White"
                
        # For colors
        if h_deg < 30 or h_deg >= 330:
            return "Red"
        elif h_deg < 90:
            return "Yellow"
        elif h_deg < 150:
            return "Green"
        elif h_deg < 210:
            return "Cyan"
        elif h_deg < 270:
            return "Blue"
        else:
            return "Magenta"
    
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
        
        # Construct the prompt
        prompt = """
        Analyze this image and provide the following information:
        1. A concise description (5 words or less) that captures the essence of the image
        2. TODO: FIX LATER Categories that apply to this image (comma-separated, choose from: nature, people, urban, food, animals, abstract, landscape, architecture, product, art, technology)
        3. The overall mood/feeling of the image (one word)
        
        Format your response as:
        Short Description: [short description]
        Categories: [category1, category2, ...]
        Mood: [mood]
        """
        
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
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
        result = response.choices[0].message.content
        
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
        
        # Extract dominant colors
        dominant_colors = self._extract_dominant_colors(image_path)
        
        # Create and return the metadata
        return ImageMetadata(
            original_filename=original_filename,
            short_description=short_description,
            categories=categories,
            dominant_colors=dominant_colors,
            mood=mood
        ) 