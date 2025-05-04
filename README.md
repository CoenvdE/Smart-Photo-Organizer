# Smart Photo Organizer for Editors

A tool that uses AI to analyze your images, generate descriptive metadata, intelligently rename files, and organize your photo collection. It can process local images or connect to your Google Drive.

## Features

- **AI Image Analysis**: Extract descriptions, categories, and mood from photos using OpenAI's services
- **Color Detection**: Automatically identify if an image is color or black & white
- **Smart Renaming**: Rename files following the format `0001-SHORT_DESCRIPTION.jpg`
- **Metadata Export**: Generate Excel/CSV file with comprehensive image metadata (categories, moods, colors)
- **Multiple Upload Methods**: 
  - Upload individual images (drag & drop multiple files)
  - Upload ZIP archives containing images (non-image files are automatically filtered out)
- **Google Drive Integration**: Authenticate via OAuth2, select folders, read/write images
- **Customization**: Define your own categories and mood options
- **Import Categories/Moods**: Import custom categories and moods from CSV or TXT files
- **Web Interface**: User-friendly Streamlit web app for both local and Google Drive processing
- **Security Features**: 
  - File size limits to prevent server overload
  - Content validation to ensure only real image files are processed
  - Protection against common upload vulnerabilities

## Privacy Note

This application uses OpenAI's services (ChatGPT/GPT-4) to analyze images. When you upload photos:
- Image data is sent to OpenAI for processing
- Images are temporarily stored on the server during processing and then deleted
- No data is permanently stored on our servers
- Please be aware of OpenAI's privacy policy regarding uploaded content

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

### Command-line Interface

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
- `--import-file FILE`: Import categories and moods from a CSV or TXT file

### Web Interface

For a more user-friendly experience, you can use the Streamlit web app:

```
streamlit run src/web_app.py
```

The web app provides:
- Local image upload and processing:
  - Upload individual images (drag & drop multiple files)
  - Upload ZIP archives containing images
- Google Drive integration
- Easy import of categories and moods
- Visual progress tracking
- Results visualization
- Downloadable ZIP of processed files (for local uploads)

### Importing Categories and Moods

You can import custom categories and moods from files in two formats:

1. **CSV Format**:
   - First column: Categories
   - Second column: Moods
   
   Example:
   ```
   nature,happy
   people,sad
   urban,calm
   food,energetic
   ```

2. **TXT Format**:
   - Categories listed first
   - Separator line with only "---"
   - Moods listed after the separator
   
   Example:
   ```
   nature
   people
   urban
   food
   ---
   happy
   sad
   calm
   energetic
   ```

### Using the Web App

1. **Enter your OpenAI API key** if prompted
2. **Choose upload method**:
   - Individual images: Drag & drop multiple files or select them using the file browser
   - ZIP archive: Upload a ZIP file containing images (non-image files are skipped)
3. **Click "Process Images"** to analyze your photos
4. **Download the results** which include:
   - Renamed image files based on content analysis
   - Excel/CSV file with comprehensive metadata (categories, moods, colors)
5. **Review the metadata summary** displayed on the page

## Project Structure

```
smart-photo-organizer/
├── requirements.txt        # Dependencies
├── drive_json/             # Google API credentials folder
│   └── credentials.json    # Google API credentials (not included in repo)
├── .env                    # Environment variables (not included in repo)
├── src/
│   ├── main.py             # Command-line entry point
│   ├── web_app.py          # Streamlit web app 
│   ├── auth/
│   │   └── google_auth.py  # Google authentication
│   ├── drive/
│   │   ├── connector.py    # Google Drive operations
│   │   └── utils.py        # Helper functions for Drive operations
│   ├── image_processing/
│   │   ├── analyzer.py     # Image analysis with AI
│   │   └── renamer.py      # Image renaming logic
│   └── metadata/
│       ├── export.py       # Metadata CSV/Excel generation
│       └── import_file.py  # Import categories/moods from files
└── tests/                  # Unit tests
```

## License

MIT