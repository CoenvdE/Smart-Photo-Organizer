# Smart Photo Organizer Usage Guide

This guide will help you get started with the Smart Photo Organizer tool.

## Prerequisites

Before you begin, make sure you have:

1. Python 3.8 or higher installed
2. A Google Cloud account with Drive API enabled
3. An OpenAI API key with access to GPT-4 Vision

## Installation

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-photo-organizer.git
cd smart-photo-organizer

# Install the package
pip install -e .
```

### Option 2: Install dependencies only

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-photo-organizer.git
cd smart-photo-organizer

# Install dependencies
pip install -r requirements.txt
```

### Option 3: Using Conda

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-photo-organizer.git
cd smart-photo-organizer

# Create and activate conda environment
conda create -n photo_organizer python=3.10 -y
conda activate photo_organizer

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. **Set up Google Drive credentials**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (Desktop application)
   - Create a folder named `drive_json` in the project root if it doesn't exist
   - Download the credentials JSON file and save it as `credentials.json` in the `drive_json` folder

2. **Set up OpenAI API key**:
   - Create a `.env` file in the project root directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

### Command-line arguments

```
python src/main.py [--input-folder-id FOLDER_ID] [--output-folder-name NAME] [--format {csv,excel}] [--categories CATEGORIES] [--moods MOODS]
```

- `--input-folder-id`: (Optional) Google Drive folder ID to process
- `--output-folder-name`: (Optional) Name for the output folder (default: "Processed Photos")
- `--format`: (Optional) Format for metadata export: 'csv' or 'excel' (default: excel)
- `--categories`: (Optional) Custom categories to use (comma-separated)
- `--moods`: (Optional) Custom moods to use (comma-separated)

### Interactive mode

If you don't provide an input folder ID, the tool will run in interactive mode:

1. First-time users will be redirected to authenticate with Google
2. The tool will display a list of folders in your Google Drive
3. Select a folder by entering its number
4. The tool will process all images in the selected folder
5. Processed images and metadata will be saved to a new folder in your Google Drive

### Example usage

```bash
# Process images with all defaults
python src/main.py

# Process a specific folder and save as CSV
python src/main.py --input-folder-id 1a2b3c4d5e6f7g8h9i0j --format csv

# Process a specific folder and customize output folder name
python src/main.py --input-folder-id 1a2b3c4d5e6f7g8h9i0j --output-folder-name "Beach Trip Photos"

# Process with custom categories and moods
python src/main.py --categories "beach,mountains,city,forest,portraits" --moods "serene,vibrant,gloomy,cheerful"
```

## Output

The tool generates two types of output:

1. **Renamed image files** in the format: `001-SHORT_DESCRIPTION.jpg`
2. **Metadata file** ("overview.xlsx" or "overview.csv") with the following columns:
   - Original Filename
   - New Filename
   - Short Description
   - Categories
   - Color Type (Color or Black & White)
   - Mood

Both outputs are saved to a new folder in your Google Drive.

## Troubleshooting

- **Authentication issues**: Delete the `token.pickle` file and restart the tool
- **API quotas**: If you hit Google Drive API quotas, wait and try again later
- **Image format errors**: Ensure you're processing standard image formats (JPEG, PNG, GIF, etc.)
- **OpenAI API errors**: Check your API key and ensure you have access to GPT-4 Vision 