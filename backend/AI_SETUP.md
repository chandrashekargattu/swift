# AI Assistant Setup Guide

## Overview

The Interstate Cab Booking application includes an advanced AI assistant powered by multiple LLM providers and RAG (Retrieval-Augmented Generation) capabilities. This guide will help you set up the AI dependencies.

## Installation

### 1. Install Dependencies

Run the installation script:

```bash
cd backend
./install_dependencies.sh
```

Or manually install:

```bash
# Activate virtual environment
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Download spacy language model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

### 2. Verify Installation

Check if all dependencies are properly installed:

```bash
python verify_ai_dependencies.py
```

## Configuration

### 1. API Keys

Add the following to your `.env` file:

```env
# OpenAI (for GPT models)
OPENAI_API_KEY=your-openai-api-key

# Anthropic (for Claude models)
ANTHROPIC_API_KEY=your-anthropic-api-key

# Google (for Gemini models)
GOOGLE_API_KEY=your-google-api-key

# Hugging Face (optional, for open-source models)
HUGGINGFACE_API_KEY=your-huggingface-api-key
```

### 2. Vector Database

The AI assistant uses ChromaDB for vector storage. It will automatically create a local database in the `chroma_db` directory.

## Features

With full AI dependencies installed, the assistant supports:

1. **Multiple LLM Providers**
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude 3)
   - Google (Gemini)
   - Hugging Face models

2. **Advanced NLP**
   - Intent classification
   - Entity recognition
   - Sentiment analysis
   - Multi-language support

3. **RAG Capabilities**
   - Knowledge base search
   - Context-aware responses
   - Document retrieval

4. **Memory Management**
   - Conversation history
   - User preferences
   - Session management

## Troubleshooting

### Common Issues

1. **"No module named 'pandas'" error**
   - Solution: Run `pip install -r requirements.txt`

2. **SpaCy model not found**
   - Solution: Run `python -m spacy download en_core_web_sm`

3. **NLTK data missing**
   - Solution: Run the NLTK download commands in the installation script

4. **PyTorch installation issues**
   - For CPU-only: `pip install torch==2.5.1`
   - For GPU: Visit [PyTorch website](https://pytorch.org/) for proper installation command

### Lightweight Mode

If you encounter issues with the full AI dependencies, the system will automatically fall back to a lightweight mode that provides basic chatbot functionality without requiring the heavy ML libraries.

## API Endpoints

The AI assistant provides the following endpoints:

- `POST /api/v1/chatbot/chat` - Authenticated chat endpoint
- `POST /api/v1/chatbot/chat/public` - Public chat endpoint (no auth required)
- `GET /api/v1/chatbot/providers` - List available AI providers
- `GET /api/v1/chatbot/health` - Check AI service health

## Testing

Test the AI assistant:

```bash
# Test public endpoint
curl -X POST http://localhost:8000/api/v1/chatbot/chat/public \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help booking a cab from Delhi to Mumbai",
    "session_id": "test123"
  }'
```

## Performance Notes

- First load may take 30-60 seconds to initialize models
- Models are cached after first load
- Consider using GPU for better performance with large models
- Adjust model parameters in `app/core/config.py` for your hardware
