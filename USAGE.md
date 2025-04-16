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

The Smart Photo Organizer can be used in two ways:
1. Command-line interface (CLI)
2. Web interface (Streamlit app)

### Command-line Interface

```
python src/main.py [--input-folder-id FOLDER_ID] [--output-folder-name NAME] [--format {csv,excel}] [--categories CATEGORIES] [--moods MOODS] [--import-file FILE]
```

- `--input-folder-id`: (Optional) Google Drive folder ID to process
- `--output-folder-name`: (Optional) Name for the output folder (default: "Processed Photos")
- `--format`: (Optional) Format for metadata export: 'csv' or 'excel' (default: excel)
- `--categories`: (Optional) Custom categories to use (comma-separated)
- `--moods`: (Optional) Custom moods to use (comma-separated)
- `--import-file`: (Optional) Import categories and moods from a CSV or TXT file

### Web Interface

For a more user-friendly experience, you can use the Streamlit web app:

```bash
streamlit run src/web_app.py
```

This will start a local web server and open your browser to the app. If it doesn't open automatically, you can navigate to http://localhost:8501.

The web app allows you to:

1. **Choose your image source**:
   - Upload local images from your computer
   - Connect to Google Drive

2. **Customize options**:
   - Choose export format (Excel or CSV)
   - Use default categories and moods
   - Import categories and moods from a file
   - Enter categories and moods manually

3. **Process and view results**:
   - Visual progress indicators
   - Preview of processed images and metadata
   - For local images: Download a ZIP file with all processed files
   - For Google Drive: Save directly to a new folder in your Drive

### Importing Categories and Moods from File

You can import custom categories and moods from external files in two formats:

#### CSV Format
Create a CSV file with:
- First column: Categories
- Second column: Moods

Example `categories_moods.csv`:
```
nature,happy
people,sad
urban,calm
food,energetic
architecture,mysterious
technology,dramatic
```

Then run:
```bash
python src/main.py --import-file categories_moods.csv
```

Or upload this file in the web interface.

#### TXT Format
Create a TXT file with:
- Categories listed first
- A separator line containing only "---"
- Moods listed after the separator

Example `categories_moods.txt`:
```
nature
people
urban
food
architecture
technology
---
happy
sad
calm
energetic
mysterious
dramatic
```

Then run:
```bash
python src/main.py --import-file categories_moods.txt
```

Or upload this file in the web interface.

### Interactive CLI Mode

If you don't provide an input folder ID in the CLI, the tool will run in interactive mode:

1. First-time users will be redirected to authenticate with Google
2. The tool will display a list of folders in your Google Drive
3. Select a folder by entering its number
4. The tool will process all images in the selected folder
5. Processed images and metadata will be saved to a new folder in your Google Drive

### Example CLI Usage

```bash
# Process images with all defaults
python src/main.py

# Process a specific folder and save as CSV
python src/main.py --input-folder-id 1a2b3c4d5e6f7g8h9i0j --format csv

# Process a specific folder and customize output folder name
python src/main.py --input-folder-id 1a2b3c4d5e6f7g8h9i0j --output-folder-name "Beach Trip Photos"

# Process with custom categories and moods
python src/main.py --categories "beach,mountains,city,forest,portraits" --moods "serene,vibrant,gloomy,cheerful"

# Process with categories and moods imported from a file
python src/main.py --import-file my_categories_moods.csv
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

Both outputs are saved to:
- A new folder in your Google Drive (when using Google Drive source)
- A downloadable ZIP file (when using local image upload in the web app)

## Troubleshooting

- **Authentication issues**: Delete the `token.pickle` file and restart the tool
- **API quotas**: If you hit Google Drive API quotas, wait and try again later
- **Image format errors**: Ensure you're processing standard image formats (JPEG, PNG, GIF, etc.)
- **OpenAI API errors**: Check your API key and ensure you have access to GPT-4 Vision
- **Import file errors**: Ensure your CSV or TXT file follows the expected format
- **Streamlit issues**: Make sure you have the latest version of Streamlit installed 