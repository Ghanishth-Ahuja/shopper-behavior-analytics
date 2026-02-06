# 🛍 Shopper Behavior Analytics & Affinity Discovery

A comprehensive e-commerce analytics platform that provides deep insights into customer behavior, personalized recommendations, and business intelligence for merchandising and marketing teams.

## 🎯 Problem Statement

Online shoppers exhibit complex behavior influenced by preferences, values, timing, and pricing. Understanding why customers behave the way they do is essential for merchandising and marketing teams to make data-driven decisions.

## 🚀 Solution Overview

This platform enables:
- **Behavioral or preference-based customer segmentation**
- **Product-category attraction analysis per segment**
- **Textual feedback interpretation and sentiment analysis**
- **Actionable insights for merchandising and marketing teams**

## 🏗 Architecture

### Backend Components

1. **Data Ingestion Engine** - Collects user behavior, transactions, reviews, and catalog data
2. **Behavioral Intelligence Engine** - Transforms raw logs into structured features, segments, affinities, and sentiment insights
3. **Decision Engine** - Generates recommendations, marketing insights, and merchandising suggestions
4. **Serving Layer** - Delivers insights, dashboards, and real-time personalization via APIs

### Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Database**: MongoDB (for semi-structured user activity data)
- **Cache/Queue**: Redis, Celery
- **ML/AI**: Scikit-learn, PyTorch, Transformers, NLTK
- **Monitoring**: Custom metrics, health checks

## 📊 Features

### 🔍 Customer Segmentation
- **RFM Analysis** (Recency, Frequency, Monetary)
- **Behavioral Clustering** using K-Means and advanced algorithms
- **Dynamic Segment Assignment** with real-time updates
- **Segment Insights** with actionable recommendations

### 🎯 Personalized Recommendations
- **Hybrid Recommendation Engine** combining:
  - Collaborative Filtering
  - Content-Based Filtering
  - Segment-Based Recommendations
  - Real-Time Session Boost
- **Explainable AI** with recommendation reasoning
- **A/B Testing** framework for algorithm optimization

### 💬 Review Intelligence
- **Sentiment Analysis** using transformer models
- **Aspect-Based Extraction** (price, quality, service, etc.)
- **Topic Modeling** for review themes
- **Trend Analysis** over time

### 📈 Business Analytics
- **Affinity Matrix** showing segment-category preferences
- **Category Lift Analysis** for cross-selling insights
- **Customer Personas** with behavioral patterns
- **Conversion Funnel Analysis**
- **Cohort Analysis** for retention insights

### ⚡ Real-Time Processing
- **Event Tracking** for user interactions
- **Feature Pipeline** for real-time feature updates
- **Background Jobs** for ML model training
- **Performance Monitoring** and health checks

## 🗂 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   └── settings.py         # Application configuration
│   ├── api/                    # API endpoints
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── sessions.py
│   │   ├── transactions.py
│   │   ├── reviews.py
│   │   ├── segmentation.py
│   │   ├── recommendations.py
│   │   ├── analytics.py
│   │   └── events.py
│   ├── models/                 # Pydantic models
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── session.py
│   │   ├── transaction.py
│   │   ├── review.py
│   │   ├── segment.py
│   │   └── user_features.py
│   ├── database/
│   │   └── mongodb.py          # MongoDB connection and collections
│   ├── services/               # Business logic layer
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   ├── session_service.py
│   │   ├── transaction_service.py
│   │   ├── review_service.py
│   │   ├── segmentation_service.py
│   │   ├── recommendation_service.py
│   │   ├── event_service.py
│   │   └── analytics_service.py
│   ├── ml/                     # Machine learning components
│   │   ├── segmentation_model.py
│   │   ├── recommendation_engine.py
│   │   └── nlp_analyzer.py
│   ├── feature_pipeline/       # Feature engineering
│   │   ├── rfm_features.py
│   │   ├── browsing_features.py
│   │   ├── category_affinity.py
│   │   └── feature_pipeline.py
│   ├── background_jobs/        # Celery tasks
│   │   ├── celery_app.py
│   │   ├── ml_tasks.py
│   │   ├── feature_tasks.py
│   │   ├── analytics_tasks.py
│   │   └── nlp_tasks.py
│   └── utils/                  # Utilities
│       ├── logger.py
│       ├── security.py
│       ├── monitoring.py
│       └── __init__.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🗄 Data Models

### Core Collections

- **users**: User profiles, demographics, segment assignments
- **sessions**: Clickstream events and browsing behavior
- **transactions**: Purchase history with items and pricing
- **products**: Catalog with categories, brands, attributes
- **reviews**: Customer feedback with sentiment analysis
- **segments**: Dynamic customer segments with characteristics
- **user_features**: ML feature store with embeddings

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- MongoDB 5.0+
- Redis 6.0+
- Node.js (for frontend, optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd shopper-behavior-analytics
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start services**
```bash
# Start MongoDB
mongod

# Start Redis
redis-server

# Start Celery worker (in separate terminal)
celery -A app.background_jobs.celery_app worker --loglevel=info

# Start Celery beat (in separate terminal)
celery -A app.background_jobs.celery_app beat --loglevel=info
```

6. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=shopper_analytics

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Models
MODEL_PATH=models/
FEATURE_STORE_PATH=features/
```

## 📊 API Endpoints

### Core APIs

- **Users**: `/api/v1/users/` - User management and analytics
- **Products**: `/api/v1/products/` - Product catalog and performance
- **Sessions**: `/api/v1/sessions/` - Browsing behavior tracking
- **Transactions**: `/api/v1/transactions/` - Purchase history
- **Reviews**: `/api/v1/reviews/` - Customer feedback analysis
- **Events**: `/api/v1/events/` - Real-time event tracking

### Analytics APIs

- **Segmentation**: `/api/v1/segmentation/` - Customer segments
- **Recommendations**: `/api/v1/recommendations/` - Personalized suggestions
- **Analytics**: `/api/v1/analytics/` - Business intelligence

## 🤖 ML Models

### Segmentation Models
- **K-Means Clustering** for baseline segmentation
- **HDBSCAN** for density-based clustering
- **Gaussian Mixture Models** for probabilistic segmentation

### Recommendation Algorithms
- **Collaborative Filtering** with matrix factorization
- **Content-Based Filtering** using product features
- **Hybrid Approach** combining multiple signals
- **Real-Time Personalization** with session data

### NLP Components
- **Sentiment Analysis** using transformer models
- **Aspect Extraction** for detailed feedback analysis
- **Topic Modeling** with Latent Dirichlet Allocation
- **Text Summarization** for review insights

## 📈 Monitoring & Observability

### Health Checks
- Database connectivity
- Redis connectivity
- System resources
- ML model availability

### Metrics Collection
- HTTP request metrics
- Database performance
- ML model performance
- System resource usage

### Logging
- Structured logging with correlation IDs
- Security event auditing
- Performance tracking
- Error monitoring

## 🔒 Security Features

- **JWT Authentication** with token blacklisting
- **Rate Limiting** per user and IP
- **Input Validation** and sanitization
- **Data Masking** for PII protection
- **Security Headers** for HTTP responses
- **Audit Logging** for compliance

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Test Categories
- **Unit Tests** for individual components
- **Integration Tests** for API endpoints
- **ML Model Tests** for algorithm validation
- **Performance Tests** for load testing

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t shopper-analytics .

# Run with Docker Compose
docker-compose up -d
```

### Production Considerations
- **Environment Variables** for configuration
- **Secrets Management** for sensitive data
- **Load Balancing** for high availability
- **Database Indexing** for performance
- **Monitoring** and alerting setup

## 📊 Usage Examples

### Customer Segmentation
```python
# Train segmentation model
POST /api/v1/segmentation/train

# Get segment insights
GET /api/v1/segmentation/segment_123/insights
```

### Personalized Recommendations
```python
# Get user recommendations
GET /api/v1/recommendations/user/user_123?limit=10

# Explain recommendation
GET /api/v1/recommendations/explain/user_123/product_456
```

### Review Analysis
```python
# Analyze product reviews
GET /api/v1/reviews/product/prod_123/insights

# Process new review
POST /api/v1/reviews/analyze
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google PREXIS Hackathon 2026
- Open source ML and NLP communities
- FastAPI and MongoDB communities

## 📞 Support

For questions and support:
- Create an issue in the repository
- Check the API documentation
- Review the configuration guide

---

**Built with ❤️ for the Google PREXIS Hackathon 2026**
