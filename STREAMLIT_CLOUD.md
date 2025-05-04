# Deploying Smart Photo Organizer to Streamlit Cloud

This guide explains how to deploy the Smart Photo Organizer application to Streamlit Cloud.

## Prerequisites

1. A GitHub account with this repository forked or cloned
2. A Streamlit Cloud account (sign up at [https://streamlit.io/cloud](https://streamlit.io/cloud))
3. An OpenAI API key

## Deployment Steps

1. Fork or clone this repository to your GitHub account
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click on "New app"
4. Select your GitHub repository, branch, and the main file path: `src/web_app.py`
5. In the "Advanced settings":
   - Add your OpenAI API key as a secret:
     ```
     OPENAI_API_KEY = "your-actual-openai-api-key"
     ```
   - Set Python version to 3.9 or 3.10

## Important Notes

1. **API Keys**: You need to provide your own OpenAI API key through the Streamlit Cloud secrets management. Do not commit your actual API keys to the repository.

2. **Temporary Files**: The app creates temporary files during image processing. Streamlit Cloud has limits on disk usage, so be mindful of this when processing large batches of images.

3. **Memory Usage**: There are limits on memory usage in the free tier of Streamlit Cloud. The app implements file size limits to help stay within these constraints.

4. **Security**: While the app implements security measures, be careful about the images you upload, as they will be processed using OpenAI's services.

## Troubleshooting

If you encounter any issues:

1. Check the app logs in Streamlit Cloud dashboard
2. Ensure all dependencies are correctly specified in requirements.txt
3. Verify your API keys are correctly set in the Streamlit secrets
4. For large files or heavy processing, consider using a paid tier of Streamlit Cloud 