# Smart Photo Organizer for Editors

A tool that connects to a user's Google Drive folder, processes images using AI to generate descriptive metadata, renames photos accordingly, and saves both the processed photos and metadata into a new folder.

?https://medium.com/the-team-of-future-learning/integrating-google-drive-api-with-python-a-step-by-step-guide-7811fcd16c44? 
drive_json/

## Features

- **Google Drive Integration**: Authenticate via OAuth2, select folders, read/write images
- **AI Image Analysis**: Extract descriptions, categories, and mood from photos
- **Color Detection**: Automatically identify if an image is color or black & white
- **Smart Renaming**: Rename files following the format `0001-SHORT_DESCRIPTION.jpg`
- **Metadata Export**: Generate Excel/CSV file with comprehensive image metadata
- **Customization**: Define your own categories and mood options

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   Or use conda:
   ```
   conda create -n photo_organizer python=3.10 -y
   conda activate photo_organizer
   pip install -r requirements.txt
   ```

3. Set up Google Drive API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials
   - Download the credentials JSON file and save as `credentials.json` in the `drive_json` folder
     (Create the folder if it doesn't exist)

4. Set up OpenAI API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

Run the main script:

```
python src/main.py [options]
```

Available options:
- `--input-folder-id FOLDER_ID`: Google Drive folder ID to process
- `--output-folder-name NAME`: Name for the output folder (default: "Processed Photos")
- `--format {csv,excel}`: Format for metadata export (default: excel)
- `--categories CATEGORIES`: Custom categories to use (comma-separated)
- `--moods MOODS`: Custom moods to use (comma-separated)

Follow the prompts to:
1. Authenticate with Google Drive
2. Select a folder containing images
3. Process the images
4. Review the generated metadata
5. Save renamed images and metadata back to Google Drive

## Project Structure

```
smart-photo-organizer/
├── requirements.txt        # Dependencies
├── drive_json/             # Google API credentials folder
│   └── credentials.json    # Google API credentials (not included in repo)
├── .env                    # Environment variables (not included in repo)
├── src/
│   ├── main.py             # Entry point
│   ├── auth/
│   │   └── google_auth.py  # Google authentication
│   ├── drive/
│   │   ├── connector.py    # Google Drive operations
│   │   └── utils.py        # Helper functions for Drive operations
│   ├── image_processing/
│   │   ├── analyzer.py     # Image analysis with AI
│   │   └── renamer.py      # Image renaming logic
│   └── metadata/
│       └── export.py       # Metadata CSV/Excel generation
└── tests/                  # Unit tests
```

## License

MIT