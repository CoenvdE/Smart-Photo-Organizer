#!/bin/bash

# Smart Photo Organizer Web App Launcher

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Launch the Streamlit app
streamlit run src/web_app.py $@

# Exit with the exit code of the streamlit command
exit $? 