#!/bin/bash

echo "Installing Interstate Cab Booking Backend Dependencies..."
echo "======================================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install main dependencies
echo "Installing main dependencies..."
pip install -r requirements.txt

# Download spacy language model
echo "Downloading spacy language model..."
python -m spacy download en_core_web_sm

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

echo ""
echo "Installation complete!"
echo ""
echo "Note: To use the AI chatbot with LLM providers, you need to set up the following environment variables:"
echo "  - OPENAI_API_KEY (for OpenAI GPT models)"
echo "  - ANTHROPIC_API_KEY (for Claude models)"
echo "  - GOOGLE_API_KEY (for Google Gemini models)"
echo ""
echo "Add these to your .env file in the backend directory."
