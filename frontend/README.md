# 🛍 Shopper Intelligence Dashboard - Frontend

A comprehensive React dashboard for analyzing customer behavior, preferences, and business insights for e-commerce platforms.

## 🎯 Purpose

This is **NOT a shopping UI**. This is a **Shopper Intelligence Dashboard Platform** used by:

- **Merchandising teams** - To understand product preferences and optimize inventory
- **Marketing teams** - To analyze customer segments and create targeted campaigns  
- **Business analysts** - To derive actionable insights from behavioral data

## 🏗 Architecture

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── api/                # API service layer
│   ├── components/         # Reusable UI components
│   │   ├── charts/        # Chart components
│   │   ├── common/        # Common UI elements
│   │   ├── segments/      # Segment-specific components
│   │   ├── recommendations/ # Recommendation components
│   │   └── affinity/       # Affinity analysis components
│   ├── context/            # React context for state management
│   ├── hooks/              # Custom React hooks
│   ├── pages/              # Page components
│   ├── layouts/            # Layout components
│   ├── styles/             # Theme and styling
│   ├── utils/              # Utility functions
│   ├── App.js              # Main application component
│   └── index.js            # Application entry point
├── package.json
├── .env.example
└── README.md
```

## 🚀 Features

### 📊 Dashboard Pages

1. **Dashboard** - High-level behavioral summary with KPIs and trends
2. **Segment Explorer** - Discover and analyze customer segments
3. **Segment Detail** - Deep insights into specific customer segments
4. **Product Affinity** - Category relationships and cross-sell opportunities
5. **Recommendation Intelligence** - ML-powered recommendation analysis
6. **Review Intelligence** - NLP-powered sentiment and aspect analysis
7. **User Explorer** - Individual customer behavior analysis

### 🎯 Key Capabilities

- **Customer Segmentation** - Behavioral and preference-based segments
- **Affinity Analysis** - Product-category relationship discovery
- **Recommendation Analytics** - ML model performance and optimization
- **Review Intelligence** - Sentiment analysis and aspect extraction
- **Real-time Updates** - Live data refresh and notifications
- **Interactive Visualizations** - Charts, heatmaps, and network graphs

## 🛠️ Tech Stack

- **React 18** - UI framework
- **Material-UI (MUI)** - Component library and theming
- **Recharts** - Chart library
- **React Query** - Data fetching and caching
- **React Router** - Navigation
- **Framer Motion** - Animations
- **Axios** - HTTP client

## 📦 Installation

1. **Install dependencies**
```bash
npm install
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start development server**
```bash
npm start
```

4. **Build for production**
```bash
npm run build
```

## 🔧 Configuration

### Environment Variables

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1

# Environment
NODE_ENV=development

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_DEBUG=true
```

### API Integration

The frontend connects to the FastAPI backend through the following API endpoints:

- `/api/v1/analytics/*` - Business intelligence data
- `/api/v1/segmentation/*` - Customer segmentation
- `/api/v1/recommendations/*` - ML recommendations
- `/api/v1/users/*` - User data and analytics

## 🎨 UI Components

### Charts
- **ConversionFunnelChart** - Sales funnel visualization
- **CategoryHeatmap** - Category affinity heatmap
- **SegmentDistributionChart** - Segment size distribution
- **RevenueTrendChart** - Revenue over time
- **RecommendationPerformanceChart** - ML model performance
- **SentimentTrendChart** - Sentiment analysis trends
- **AspectSentimentChart** - Aspect-based sentiment analysis

### Data Display
- **MetricCard** - KPI display with trends
- **SegmentCard** - Customer segment overview
- **RecommendationList** - Product recommendations
- **CrossSellTable** - Cross-sell opportunities

### Layout
- **Navbar** - Main navigation with notifications
- **Sidebar** - Navigation menu with filters
- **ErrorBoundary** - Error handling and recovery

## 🎯 State Management

Uses React Context API for global state:

- **AppContext** - Global application state
- **Authentication** - User login state
- **Filters** - Dashboard filters and selections
- **Theme** - Light/dark mode preferences

## 📊 Data Visualization

### Chart Types
- **Line Charts** - Trends over time
- **Bar Charts** - Comparisons and rankings
- **Pie Charts** - Distribution and proportions
- **Radar Charts** - Multi-dimensional comparisons
- **Heatmaps** - Intensity and correlation matrices
- **Network Graphs** - Relationship visualization

### Color Schemes
- **Sentiment Colors** - Positive (green), Negative (red), Neutral (grey)
- **Performance Colors** - Success (green), Warning (orange), Error (red)
- **Segment Colors** - Distinct colors for customer segments

## 🔍 User Experience

### Navigation Flow
1. **Marketing Analyst**: Dashboard → Segment Explorer → Segment Detail → Campaign Suggestion
2. **Merchandiser**: Dashboard → Affinity Page → Product Bundles → Recommendation Performance
3. **Product Manager**: Review Intelligence → Customer Complaints → Product Improvement

### Interactive Features
- **Real-time Updates** - Auto-refresh data every 30-60 seconds
- **Drill-down Navigation** - Click to explore deeper insights
- **Filter Controls** - Date range, segment, category filters
- **Export Options** - Download charts and data (planned)

## 📱 Responsive Design

- **Mobile** - Optimized for tablets and phones
- **Desktop** - Full-featured dashboard experience
- **Adaptive Layout** - Components adjust to screen size
- **Touch-friendly** - Mobile-optimized interactions

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:e2e
```

### Coverage
```bash
npm run test:coverage
```

## 🚀 Performance

### Optimizations
- **Lazy Loading** - Components load on demand
- **Memoization** - Expensive computations cached
- **Debounced Filters** - Search and filter optimization
- **Virtualized Tables** - Large dataset handling
- **Image Optimization** - Efficient image loading

### Monitoring
- **Page Load Time** - Track loading performance
- **API Latency** - Monitor backend response times
- **User Interactions** - Track user behavior patterns

## 🔒 Security

### Features
- **JWT Authentication** - Secure user sessions
- **Input Validation** - Sanitize all user inputs
- **Rate Limiting** - Prevent API abuse
- **Data Masking** - PII protection in UI
- **Security Headers** - HTTP security headers

### Best Practices
- **Environment Variables** - No hardcoded secrets
- **HTTPS Only** - Secure data transmission
- **CORS Configuration** - Proper cross-origin settings
- **Content Security Policy** - Prevent XSS attacks

## 🎨 Customization

### Theme Configuration
- **Light/Dark Mode** - Toggle between themes
- **Color Palette** - Custom brand colors
- **Typography** - Custom font families
- **Component Styling** - Override MUI defaults

### Branding
- **Logo** - Replace with company logo
- **Colors** - Match brand guidelines
- **Typography** - Use brand fonts
- **Icons** - Custom icon library

## 📈 Analytics

### Tracked Metrics
- **Page Views** - Dashboard page usage
- **Feature Usage** - Most used features
- **User Sessions** - Session duration and frequency
- **Error Rates** - Application errors and failures

### Business Metrics
- **Conversion Rate** - Dashboard to action conversion
- **User Engagement** - Time spent in dashboard
- **Feature Adoption** - New feature usage
- **Data Freshness** - Data update frequency

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Environment Setup
- **Development** - `npm start`
- **Staging** - `npm run build && npm run test`
- **Production** - `npm run build && npm run test:e2e`

### Hosting Options
- **Vercel** - Recommended for React apps
- **Netlify** - Static site hosting
- **AWS S3** - Cloud storage hosting
- **Docker** - Containerized deployment

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Code review and merge

### Code Standards
- **ESLint** - Code linting and formatting
- **Prettier** - Code formatting
- **TypeScript** - Type checking
- **Husky** - Git hooks for quality

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Google PREXIS Hackathon 2026** - Original project inspiration
- **Material-UI Team** - Component library
- **Recharts Team** - Chart library
- **React Community** - Framework and ecosystem

---

**Built with ❤️ for data-driven business intelligence** 🚀
