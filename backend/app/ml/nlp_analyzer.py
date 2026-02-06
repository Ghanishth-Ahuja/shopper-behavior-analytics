from typing import Dict, List, Optional, Tuple
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import joblib
import os
from datetime import datetime
from app.database.mongodb import MongoDB, Collections
from app.models.review import ReviewAnalysis


# Download NLTK data (only once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')


class NLPAnalyzer:
    """NLP analyzer for review sentiment, aspect extraction, and topic modeling"""
    
    def __init__(self, model_path: str = "models/nlp/"):
        self.model_path = model_path
        self.db = MongoDB.get_database()
        
        # Initialize NLP components
        self.sia = SentimentIntensityAnalyzer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Aspect extraction patterns
        self.aspect_patterns = {
            'price': [r'price', r'cost', r'expensive', r'cheap', r'affordable', r'value'],
            'quality': [r'quality', r'durable', r'well-made', r'flimsy', r'sturdy'],
            'service': [r'service', r'support', r'help', r'staff', r'customer'],
            'shipping': [r'shipping', r'delivery', r'packaging', r'arrived'],
            'features': [r'feature', r'functionality', r'capability', r'option'],
            'design': [r'design', r'look', r'appearance', r'style', r'color'],
            'usability': [r'easy', r'difficult', r'use', r'operate', r'intuitive']
        }
        
        # Topic modeling components
        self.topic_vectorizer = None
        self.topic_model = None
        
        # Ensure model directory exists
        os.makedirs(model_path, exist_ok=True)
    
    async def analyze_review(self, review_text: str) -> ReviewAnalysis:
        """Comprehensive review analysis"""
        try:
            # Basic sentiment analysis
            sentiment_score = self._calculate_sentiment_score(review_text)
            sentiment = self._get_sentiment_label(sentiment_score)
            
            # Aspect-based sentiment analysis
            aspects = await self._extract_aspects(review_text)
            
            # Topic modeling
            topics = await self._extract_topics(review_text)
            
            # Confidence score
            confidence = self._calculate_confidence(sentiment_score, aspects)
            
            return ReviewAnalysis(
                review_id="",  # Will be filled by caller
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                aspects=aspects,
                topics=topics,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"Error analyzing review: {e}")
            return ReviewAnalysis(
                review_id="",
                sentiment="neutral",
                sentiment_score=0.0,
                aspects={},
                topics=[],
                confidence=0.0
            )
    
    async def analyze_product_reviews(self, product_id: str) -> Dict:
        """Analyze all reviews for a product"""
        try:
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find({"product_id": product_id})
            reviews = await cursor.to_list(length=None)
            
            if not reviews:
                return {
                    "product_id": product_id,
                    "total_reviews": 0,
                    "avg_rating": 0,
                    "sentiment_distribution": {},
                    "aspect_insights": {},
                    "top_topics": [],
                    "summary": "No reviews available"
                }
            
            # Analyze each review
            analyses = []
            for review in reviews:
                analysis = await self.analyze_review(review.get('review_text', ''))
                analysis.review_id = review.get('review_id', '')
                analyses.append(analysis)
            
            # Aggregate insights
            insights = await self._aggregate_review_insights(analyses, reviews)
            insights["product_id"] = product_id
            insights["total_reviews"] = len(reviews)
            insights["avg_rating"] = np.mean([r.get('rating', 0) for r in reviews])
            
            return insights
            
        except Exception as e:
            print(f"Error analyzing product reviews: {e}")
            return {"error": str(e)}
    
    async def analyze_segment_sentiment(self, segment_id: str) -> Dict:
        """Analyze sentiment patterns for a user segment"""
        try:
            # Get users in segment
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({"segment_id": segment_id})
            users = await cursor.to_list(length=None)
            
            if not users:
                return {"segment_id": segment_id, "error": "No users found in segment"}
            
            user_ids = [user['user_id'] for user in users]
            
            # Get reviews from these users
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find({"user_id": {"$in": user_ids}})
            reviews = await cursor.to_list(length=None)
            
            if not reviews:
                return {
                    "segment_id": segment_id,
                    "total_reviews": 0,
                    "sentiment_profile": {},
                    "aspect_preferences": {},
                    "summary": "No reviews from segment users"
                }
            
            # Analyze reviews
            analyses = []
            for review in reviews:
                analysis = await self.analyze_review(review.get('review_text', ''))
                analyses.append(analysis)
            
            # Aggregate segment insights
            segment_insights = await self._aggregate_segment_insights(analyses)
            segment_insights["segment_id"] = segment_id
            segment_insights["total_reviews"] = len(reviews)
            
            return segment_insights
            
        except Exception as e:
            print(f"Error analyzing segment sentiment: {e}")
            return {"segment_id": segment_id, "error": str(e)}
    
    async def train_topic_model(self, min_reviews: int = 100) -> Dict:
        """Train topic modeling on existing reviews"""
        try:
            # Get all reviews
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find({})
            reviews = await cursor.to_list(length=None)
            
            if len(reviews) < min_reviews:
                return {"status": "error", "message": f"Need at least {min_reviews} reviews for training"}
            
            # Extract review texts
            review_texts = [review.get('review_text', '') for review in reviews]
            review_texts = [text for text in review_texts if len(text) > 10]  # Filter short reviews
            
            if len(review_texts) < min_reviews:
                return {"status": "error", "message": f"Need at least {min_reviews} substantial reviews for training"}
            
            # Create TF-IDF vectorizer
            self.topic_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            
            # Fit vectorizer and transform texts
            doc_term_matrix = self.topic_vectorizer.fit_transform(review_texts)
            
            # Train LDA model
            self.topic_model = LatentDirichletAllocation(
                n_components=10,  # 10 topics
                random_state=42,
                max_iter=100
            )
            
            self.topic_model.fit(doc_term_matrix)
            
            # Save models
            await self._save_topic_models()
            
            # Get topic words
            topic_words = self._get_topic_words()
            
            return {
                "status": "success",
                "topics_trained": 10,
                "reviews_used": len(review_texts),
                "topic_words": topic_words
            }
            
        except Exception as e:
            print(f"Error training topic model: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score using VADER"""
        try:
            scores = self.sia.polarity_scores(text)
            return scores['compound']
        except Exception:
            return 0.0
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score >= 0.05:
            return "positive"
        elif score <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    async def _extract_aspects(self, text: str) -> Dict[str, float]:
        """Extract aspects and their sentiment scores"""
        try:
            aspects = {}
            text_lower = text.lower()
            
            for aspect, patterns in self.aspect_patterns.items():
                aspect_sentiments = []
                
                for pattern in patterns:
                    # Find sentences containing aspect keywords
                    sentences = sent_tokenize(text)
                    for sentence in sentences:
                        if re.search(pattern, sentence.lower()):
                            # Calculate sentiment for this sentence
                            sentiment = self._calculate_sentiment_score(sentence)
                            aspect_sentiments.append(sentiment)
                
                # Average sentiment for this aspect
                if aspect_sentiments:
                    aspects[aspect] = np.mean(aspect_sentiments)
            
            return aspects
            
        except Exception as e:
            print(f"Error extracting aspects: {e}")
            return {}
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics using trained topic model"""
        try:
            if not self.topic_model or not self.topic_vectorizer:
                await self._load_topic_models()
            
            if not self.topic_model or not self.topic_vectorizer:
                return []
            
            # Transform text
            text_vector = self.topic_vectorizer.transform([text])
            
            # Get topic distribution
            topic_distribution = self.topic_model.transform(text_vector)[0]
            
            # Get top topics
            top_topic_indices = np.argsort(topic_distribution)[-3:][::-1]  # Top 3 topics
            
            # Get topic words for these topics
            topics = []
            for topic_idx in top_topic_indices:
                if topic_distribution[topic_idx] > 0.1:  # Threshold
                    topic_words = self._get_topic_words_for_topic(topic_idx)
                    topics.append(f"Topic {topic_idx}: {', '.join(topic_words[:3])}")
            
            return topics
            
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return []
    
    def _calculate_confidence(self, sentiment_score: float, aspects: Dict) -> float:
        """Calculate confidence in analysis"""
        try:
            # Base confidence from sentiment strength
            base_confidence = abs(sentiment_score)
            
            # Boost confidence if aspects found
            aspect_boost = min(len(aspects) * 0.1, 0.3)
            
            # Total confidence
            confidence = min(base_confidence + aspect_boost, 1.0)
            
            return max(confidence, 0.1)  # Minimum confidence
            
        except Exception:
            return 0.5
    
    async def _aggregate_review_insights(self, analyses: List[ReviewAnalysis], reviews: List[Dict]) -> Dict:
        """Aggregate insights from multiple reviews"""
        try:
            # Sentiment distribution
            sentiments = [analysis.sentiment for analysis in analyses]
            sentiment_counts = Counter(sentiments)
            sentiment_distribution = {
                "positive": sentiment_counts.get("positive", 0),
                "negative": sentiment_counts.get("negative", 0),
                "neutral": sentiment_counts.get("neutral", 0)
            }
            
            # Aspect insights
            all_aspects = defaultdict(list)
            for analysis in analyses:
                for aspect, score in analysis.aspects.items():
                    all_aspects[aspect].append(score)
            
            aspect_insights = {}
            for aspect, scores in all_aspects.items():
                aspect_insights[aspect] = {
                    "avg_sentiment": np.mean(scores),
                    "mention_count": len(scores),
                    "sentiment_label": self._get_sentiment_label(np.mean(scores))
                }
            
            # Top topics
            all_topics = []
            for analysis in analyses:
                all_topics.extend(analysis.topics)
            
            topic_counts = Counter(all_topics)
            top_topics = [topic for topic, count in topic_counts.most_common(5)]
            
            # Generate summary
            summary = self._generate_summary(sentiment_distribution, aspect_insights)
            
            return {
                "sentiment_distribution": sentiment_distribution,
                "aspect_insights": aspect_insights,
                "top_topics": top_topics,
                "summary": summary
            }
            
        except Exception as e:
            print(f"Error aggregating review insights: {e}")
            return {}
    
    async def _aggregate_segment_insights(self, analyses: List[ReviewAnalysis]) -> Dict:
        """Aggregate insights for a segment"""
        try:
            # Sentiment profile
            sentiments = [analysis.sentiment for analysis in analyses]
            sentiment_counts = Counter(sentiments)
            total_reviews = len(analyses)
            
            sentiment_profile = {
                "positive_percentage": (sentiment_counts.get("positive", 0) / total_reviews) * 100,
                "negative_percentage": (sentiment_counts.get("negative", 0) / total_reviews) * 100,
                "neutral_percentage": (sentiment_counts.get("neutral", 0) / total_reviews) * 100
            }
            
            # Aspect preferences
            all_aspects = defaultdict(list)
            for analysis in analyses:
                for aspect, score in analysis.aspects.items():
                    all_aspects[aspect].append(score)
            
            aspect_preferences = {}
            for aspect, scores in all_aspects.items():
                aspect_preferences[aspect] = {
                    "avg_sentiment": np.mean(scores),
                    "importance": len(scores) / total_reviews,  # How often mentioned
                    "sentiment_label": self._get_sentiment_label(np.mean(scores))
                }
            
            # Generate segment summary
            summary = self._generate_segment_summary(sentiment_profile, aspect_preferences)
            
            return {
                "sentiment_profile": sentiment_profile,
                "aspect_preferences": aspect_preferences,
                "summary": summary
            }
            
        except Exception as e:
            print(f"Error aggregating segment insights: {e}")
            return {}
    
    def _generate_summary(self, sentiment_distribution: Dict, aspect_insights: Dict) -> str:
        """Generate a summary of product reviews"""
        try:
            total_reviews = sum(sentiment_distribution.values())
            positive_pct = (sentiment_distribution.get("positive", 0) / total_reviews) * 100
            
            summary = f"Based on {total_reviews} reviews, {positive_pct:.1f}% are positive. "
            
            # Add key insights
            if aspect_insights:
                top_aspect = max(aspect_insights.items(), key=lambda x: len(x[1]))
                aspect_name, aspect_data = top_aspect
                aspect_sentiment = aspect_data.get("sentiment_label", "neutral")
                
                summary += f"Customers frequently mention {aspect_name} with {aspect_sentiment} sentiment. "
            
            return summary
            
        except Exception:
            return "Summary not available"
    
    def _generate_segment_summary(self, sentiment_profile: Dict, aspect_preferences: Dict) -> str:
        """Generate a summary of segment sentiment"""
        try:
            positive_pct = sentiment_profile.get("positive_percentage", 0)
            
            summary = f"This segment shows {positive_pct:.1f}% positive sentiment in reviews. "
            
            if aspect_preferences:
                # Find most important aspect
                most_important = max(aspect_preferences.items(), key=lambda x: x[1].get("importance", 0))
                aspect_name, aspect_data = most_important
                importance = aspect_data.get("importance", 0) * 100
                
                summary += f"They care most about {aspect_name} ({importance:.1f}% mention rate). "
            
            return summary
            
        except Exception:
            return "Segment summary not available"
    
    def _get_topic_words(self, n_words: int = 10) -> List[List[str]]:
        """Get top words for all topics"""
        try:
            if not self.topic_model or not self.topic_vectorizer:
                return []
            
            feature_names = self.topic_vectorizer.get_feature_names_out()
            topic_words = []
            
            for topic_idx, topic in enumerate(self.topic_model.components_):
                top_indices = topic.argsort()[-n_words:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                topic_words.append(top_words)
            
            return topic_words
            
        except Exception as e:
            print(f"Error getting topic words: {e}")
            return []
    
    def _get_topic_words_for_topic(self, topic_idx: int, n_words: int = 5) -> List[str]:
        """Get top words for a specific topic"""
        try:
            if not self.topic_model or not self.topic_vectorizer:
                return []
            
            feature_names = self.topic_vectorizer.get_feature_names_out()
            topic = self.topic_model.components_[topic_idx]
            
            top_indices = topic.argsort()[-n_words:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            
            return top_words
            
        except Exception as e:
            print(f"Error getting topic words for topic {topic_idx}: {e}")
            return []
    
    async def _save_topic_models(self) -> None:
        """Save trained topic models"""
        try:
            vectorizer_file = os.path.join(self.model_path, "topic_vectorizer.joblib")
            model_file = os.path.join(self.model_path, "topic_model.joblib")
            
            joblib.dump(self.topic_vectorizer, vectorizer_file)
            joblib.dump(self.topic_model, model_file)
            
            print(f"Topic models saved to {self.model_path}")
            
        except Exception as e:
            print(f"Error saving topic models: {e}")
    
    async def _load_topic_models(self) -> bool:
        """Load trained topic models"""
        try:
            vectorizer_file = os.path.join(self.model_path, "topic_vectorizer.joblib")
            model_file = os.path.join(self.model_path, "topic_model.joblib")
            
            if os.path.exists(vectorizer_file) and os.path.exists(model_file):
                self.topic_vectorizer = joblib.load(vectorizer_file)
                self.topic_model = joblib.load(model_file)
                print(f"Topic models loaded from {self.model_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error loading topic models: {e}")
            return False
    
    async def get_sentiment_trends(self, product_id: str, days: int = 30) -> Dict:
        """Get sentiment trends over time for a product"""
        try:
            from datetime import timedelta
            
            reviews_collection = self.db[Collections.REVIEWS]
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = reviews_collection.find({
                "product_id": product_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            reviews = await cursor.to_list(length=None)
            
            # Group by day
            daily_sentiments = defaultdict(list)
            
            for review in reviews:
                date = review.get('timestamp', datetime.utcnow()).date()
                sentiment = self._calculate_sentiment_score(review.get('review_text', ''))
                daily_sentiments[date].append(sentiment)
            
            # Calculate daily averages
            sentiment_trends = {}
            for date, sentiments in daily_sentiments.items():
                sentiment_trends[str(date)] = {
                    "avg_sentiment": np.mean(sentiments),
                    "review_count": len(sentiments)
                }
            
            return {
                "product_id": product_id,
                "period_days": days,
                "sentiment_trends": sentiment_trends
            }
            
        except Exception as e:
            print(f"Error getting sentiment trends: {e}")
            return {}
