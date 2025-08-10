# RideSwift - Premium Interstate Cab Booking

A modern, responsive cab booking website built with Next.js, TypeScript, and Tailwind CSS. Book comfortable and reliable cabs for interstate and local travel.

## Features

### User Features
- 🚗 **Multi-city Support**: Book cabs between major cities across India
- 💰 **Transparent Pricing**: Clear pricing with detailed breakdown
- 🎨 **Beautiful UI**: Modern, responsive design with smooth animations
- 📱 **Mobile Friendly**: Fully responsive across all devices
- 🚀 **Fast Performance**: Built with Next.js for optimal performance
- 🔒 **Type Safe**: Written in TypeScript for better code quality
- 👤 **User Authentication**: Secure sign-up and sign-in with JWT
- ⏰ **Auto Sign-out**: Automatic session timeout for security
- 📧 **Email Notifications**: Booking confirmations and updates
- 📱 **SMS Notifications**: Real-time updates via SMS
- 🤖 **AI-Powered Assistant**: Advanced chatbot with natural language understanding
  - Multiple AI providers (OpenAI GPT-4, Anthropic Claude, Google Gemini)
  - Intelligent booking assistance and route recommendations
  - Emotion-aware responses for better customer experience
  - Voice input support for hands-free interaction
  - Real-time fare calculations and availability checks

### Technical Features
- 🗄️ **MongoDB Integration**: Scalable NoSQL database
- 🚀 **Redis Caching**: Fast API responses and session storage
- 📬 **Async Task Processing**: Background jobs with Celery
- 🔐 **API Rate Limiting**: Protection against abuse
- 🌐 **API Gateway Ready**: Kong configuration included
- 🔍 **Comprehensive Testing**: Unit, integration, and E2E tests
- 📊 **Health Monitoring**: Built-in health check endpoints
- 🎯 **Error Handling**: Graceful error boundaries and recovery
- 🔄 **API Versioning**: Future-proof API design
- 📝 **Structured Logging**: JSON logging for better observability

## Tech Stack

### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Forms**: React Hook Form
- **Date Handling**: date-fns

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Caching**: Redis
- **Message Queue**: Celery + Redis
- **Authentication**: JWT
- **API Gateway**: Kong (optional)

### AI/ML Stack (Optional)
- **LLM Frameworks**: LangChain, LangChain Community
- **AI Providers**: OpenAI, Anthropic, Google AI
- **NLP**: spaCy, NLTK, Transformers
- **Embeddings**: Sentence Transformers, HuggingFace
- **Vector Databases**: ChromaDB, FAISS, Pinecone
- **ML Libraries**: scikit-learn, PyTorch

### Testing
- **Unit/Integration**: pytest
- **E2E**: Playwright

## Getting Started

### Prerequisites

- Node.js 20.0.0 or higher
- Python 3.11 or higher
- MongoDB
- Redis (optional, for caching and async tasks)
- npm or yarn

### Installation

#### Frontend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/interstate-cab-booking.git
cd interstate-cab-booking
```

2. Install frontend dependencies:
```bash
npm install
```

3. Run the frontend development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp env.example .env
```

5. Update `.env` with your configurations

6. Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

#### Optional Services

**Redis** (for caching and sessions):
```bash
docker run -d -p 6379:6379 redis:latest
```

**Celery Worker** (for async tasks):
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

**Celery Beat** (for periodic tasks):
```bash
cd backend
celery -A app.core.celery_app beat --loglevel=info
```

### AI Chatbot Setup (Optional)

The application includes an advanced AI chatbot that works out of the box with basic functionality. For enhanced AI features:

1. **Basic Setup (No API Keys Required)**
   - The chatbot will work with rule-based responses
   - Provides booking assistance, pricing info, and support

2. **Advanced Setup (Recommended)**

   Add one or more AI provider API keys to your `.env` file:

   ```bash
   # Choose one or more providers
   OPENAI_API_KEY=your-openai-api-key        # For GPT-4
   ANTHROPIC_API_KEY=your-anthropic-api-key  # For Claude
   GOOGLE_API_KEY=your-google-api-key        # For Gemini
   ```

3. **Install AI Dependencies**

   For full AI capabilities, install additional dependencies:
   
   ```bash
   cd backend
   source venv/bin/activate
   
   # Essential AI packages
   pip install langchain langchain-community langchain-openai
   pip install chromadb sentence-transformers
   pip install spacy nltk
   
   # Download language models
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt stopwords wordnet
   ```

4. **Features by Setup Level**

   - **Basic (No API Keys)**: Intent detection, FAQ responses, booking guidance
   - **With API Keys**: Natural language understanding, context awareness, personalized responses
   - **Full Installation**: RAG capabilities, emotion detection, multi-language support

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### E2E Tests

```bash
# Install Playwright browsers
npx playwright install

# Run E2E tests
npm run test:e2e

# Run with UI mode
npm run test:e2e:ui

# Debug tests
npm run test:e2e:debug
```

## Deployment

### Deploy to Vercel (Recommended)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

Follow the prompts to deploy your application.

### Deploy to Netlify

1. Build the project:
```bash
npm run build
```

2. Install Netlify CLI:
```bash
npm i -g netlify-cli
```

3. Deploy:
```bash
netlify deploy --prod --dir=.next
```

### Manual Deployment

1. Build the project:
```bash
npm run build
```

2. The build output will be in the `.next` directory
3. Deploy this directory to any Node.js hosting service

## Project Structure

```
interstate-cab-booking/
├── src/
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   │   ├── booking/      # Booking related components
│   │   ├── layout/       # Layout components
│   │   └── ui/          # UI components
│   ├── data/            # Static data (locations, cabs)
│   ├── lib/             # Utility functions
│   └── types/           # TypeScript types
├── public/              # Static assets
└── package.json         # Project dependencies
```

## Features Overview

### Booking Process
1. **Route Selection**: Choose pickup and drop locations from 30+ cities
2. **Date & Time**: Select your travel date and preferred pickup time
3. **Vehicle Selection**: Choose from Sedan, SUV, Luxury, or Tempo Traveller
4. **Price Review**: Transparent pricing with GST included
5. **Confirmation**: Review and confirm your booking

### Available Routes
- Mumbai ↔ Pune
- Delhi ↔ Jaipur
- Bangalore ↔ Chennai
- And many more interstate routes

### Vehicle Options
- **Sedan**: 4 passengers, ₹12/km
- **SUV**: 6 passengers, ₹16/km
- **Luxury**: 4 passengers, ₹25/km
- **Tempo Traveller**: 12 passengers, ₹22/km

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For support, email support@rideswift.com or call 800-894-2278.