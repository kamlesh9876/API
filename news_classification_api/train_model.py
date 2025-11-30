"""
Training script for Fake News Detection Model
This script demonstrates how to train a machine learning model for fake news classification.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class FakeNewsFeatureExtractor:
    """Extract features from text for fake news detection"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.sensational_words = [
            'shocking', 'unbelievable', 'miracle', 'breakthrough', 'conspiracy',
            'cover-up', 'secret', 'revealed', 'exposed', 'hidden', 'scandal',
            'outrageous', 'incredible', 'amazing', 'stunning', 'mind-blowing'
        ]
        self.clickbait_words = [
            'you won\'t believe', 'shocking results', 'doctors hate this',
            'one weird trick', 'this will change everything', 'never seen before'
        ]
    
    def extract_text_features(self, text):
        """Extract basic text features"""
        features = {}
        
        # Basic counts
        features['text_length'] = len(text)
        features['word_count'] = len(text.split())
        features['char_count'] = len(text.replace(' ', ''))
        features['avg_word_length'] = features['char_count'] / max(features['word_count'], 1)
        
        # Punctuation
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['period_count'] = text.count('.')
        features['comma_count'] = text.count(',')
        
        # Capitalization
        features['upper_count'] = sum(1 for c in text if c.isupper())
        features['upper_ratio'] = features['upper_count'] / max(len(text), 1)
        
        # Sensational words
        text_lower = text.lower()
        features['sensational_count'] = sum(1 for word in self.sensational_words if word in text_lower)
        features['clickbait_count'] = sum(1 for phrase in self.clickbait_words if phrase in text_lower)
        
        # Readability (simplified)
        sentences = text.split('.')
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        features['avg_sentence_length'] = avg_sentence_length
        
        return features
    
    def extract_linguistic_features(self, text):
        """Extract linguistic features"""
        features = {}
        
        # Tokenize
        tokens = word_tokenize(text.lower())
        tokens = [t for t in tokens if t.isalpha() and t not in self.stop_words]
        
        # Part of speech tags
        pos_tags = nltk.pos_tag(tokens)
        
        # Count different POS types
        pos_counts = Counter(tag for word, tag in pos_tags)
        total_pos = sum(pos_counts.values())
        
        features['noun_ratio'] = pos_counts.get('NN', 0) / max(total_pos, 1)
        features['verb_ratio'] = pos_counts.get('VB', 0) / max(total_pos, 1)
        features['adj_ratio'] = pos_counts.get('JJ', 0) / max(total_pos, 1)
        
        # Vocabulary richness
        unique_words = len(set(tokens))
        features['vocab_richness'] = unique_words / max(len(tokens), 1)
        
        return features

def load_sample_data():
    """Load or create sample training data"""
    # In production, load real dataset from CSV/JSON
    # For demo, create synthetic data
    
    real_news = [
        "The Federal Reserve announced today a quarter-point increase in the federal funds rate.",
        "Scientists have discovered a new species of dinosaur in Argentina, according to a study published in Nature.",
        "The unemployment rate fell to 3.5% in the latest report from the Bureau of Labor Statistics.",
        "Researchers at MIT have developed a new battery technology that could revolutionize electric vehicles.",
        "The United Nations Climate Summit concluded with agreements on carbon emission reductions."
    ]
    
    fake_news = [
        "SHOCKING! Doctors hate this one weird trick that cures all diseases instantly!",
        "BREAKING: Aliens have landed and the government is covering it up! You won't believe this!",
        "MIRACLE CURE discovered that big pharma doesn't want you to know about!",
        "CONSPIRACY REVEALED: The moon landing was faked and here's the proof!",
        "UNBELIEVABLE: This one food can make you lose 50 pounds in one week!"
    ]
    
    # Create DataFrame
    data = []
    for text in real_news:
        data.append({'text': text, 'label': 'real'})
    for text in fake_news:
        data.append({'text': text, 'label': 'fake'})
    
    # Add more variations for better training
    for _ in range(10):  # Duplicate and vary
        for text, label in [(real_news[0], 'real'), (fake_news[0], 'fake')]:
            varied_text = text + " Additional context and details."
            data.append({'text': varied_text, 'label': label})
    
    return pd.DataFrame(data)

def prepare_features(df):
    """Prepare features for training"""
    extractor = FakeNewsFeatureExtractor()
    
    # Extract text features
    text_features = df['text'].apply(extractor.extract_text_features)
    text_features_df = pd.DataFrame(text_features.tolist())
    
    # Extract linguistic features
    linguistic_features = df['text'].apply(extractor.extract_linguistic_features)
    linguistic_features_df = pd.DataFrame(linguistic_features.tolist())
    
    # Combine features
    features_df = pd.concat([text_features_df, linguistic_features_df], axis=1)
    
    # Fill NaN values
    features_df = features_df.fillna(0)
    
    return features_df

def train_models(X_train, y_train):
    """Train multiple models"""
    models = {}
    
    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    models['random_forest'] = rf
    
    # Naive Bayes
    nb = MultinomialNB()
    nb.fit(X_train, y_train)
    models['naive_bayes'] = nb
    
    # Logistic Regression
    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X_train, y_train)
    models['logistic_regression'] = lr
    
    # SVM
    svm = SVC(probability=True, random_state=42)
    svm.fit(X_train, y_train)
    models['svm'] = svm
    
    return models

def evaluate_models(models, X_test, y_test):
    """Evaluate all models"""
    results = {}
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        
        results[name] = {
            'accuracy': accuracy,
            'classification_report': report,
            'model': model
        }
    
    return results

def save_best_model(results, model_path='models/fake_news_detector.pkl'):
    """Save the best performing model"""
    best_model_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
    best_model = results[best_model_name]['model']
    
    # Create models directory if it doesn't exist
    import os
    os.makedirs('models', exist_ok=True)
    
    # Save model
    joblib.dump(best_model, model_path)
    
    print(f"Best model: {best_model_name} with accuracy: {results[best_model_name]['accuracy']:.3f}")
    print(f"Model saved to: {model_path}")
    
    return best_model_name, results[best_model_name]['accuracy']

def main():
    """Main training pipeline"""
    print("Starting Fake News Detection Model Training...")
    
    # Load data
    print("Loading data...")
    df = load_sample_data()
    print(f"Dataset shape: {df.shape}")
    print(f"Class distribution: {df['label'].value_counts()}")
    
    # Prepare features
    print("Extracting features...")
    X = prepare_features(df)
    y = df['label']
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Features: {list(X.columns)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}")
    
    # Train models
    print("Training models...")
    models = train_models(X_train, y_train)
    
    # Evaluate models
    print("Evaluating models...")
    results = evaluate_models(models, X_test, y_test)
    
    # Print results
    print("\nModel Performance:")
    for name, result in results.items():
        print(f"{name}: {result['accuracy']:.3f}")
    
    # Save best model
    best_model_name, best_accuracy = save_best_model(results)
    
    print(f"\nTraining completed!")
    print(f"Best model: {best_model_name}")
    print(f"Best accuracy: {best_accuracy:.3f}")
    
    # Feature importance (for Random Forest)
    if 'random_forest' in models:
        rf_model = models['random_forest']
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Important Features:")
        print(feature_importance.head(10))

if __name__ == "__main__":
    main()
