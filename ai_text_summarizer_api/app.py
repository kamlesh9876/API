from fastapi import FastAPI, HTTPException, Depends, Query, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid
import os
import tempfile
import asyncio
import re
from collections import Counter
import logging

# ML and NLP imports
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    pipeline,
    AutoModelForSequenceClassification
)
from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
import spacy

app = FastAPI(title="AI Text Summarizer API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download NLTK data (only if not already downloaded)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('chunkers/maxent_ne_chunker')
except LookupError:
    nltk.download('maxent_ne_chunker')

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

# Enums
class SummaryType(str, Enum):
    ABSTRACTIVE = "abstractive"  # Generate new sentences
    EXTRACTIVE = "extractive"    # Extract important sentences
    BULLET_POINTS = "bullet_points"  # Bullet point format
    HEADLINE = "headline"  # Single sentence summary
    KEY_POINTS = "key_points"  # Main points only

class SummaryLength(str, Enum):
    SHORT = "short"  # ~50 words
    MEDIUM = "medium"  # ~150 words
    LONG = "long"  # ~300 words
    CUSTOM = "custom"  # Custom length

class Language(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"
    AUTO = "auto"  # Auto-detect

# Pydantic models
class TextSummaryRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=50000, description="Text to summarize")
    summary_type: SummaryType = SummaryType.ABSTRACTIVE
    summary_length: SummaryLength = SummaryLength.MEDIUM
    max_length: Optional[int] = Field(None, ge=10, le=1000)
    min_length: Optional[int] = Field(None, ge=5, le=500)
    language: Language = Language.AUTO
    extract_keywords: bool = True
    keyword_count: int = Field(10, ge=1, le=50)
    bullet_points_count: int = Field(5, ge=1, le=20)
    include_statistics: bool = False

class KeywordExtraction(BaseModel):
    keywords: List[str]
    key_phrases: List[str]
    entities: List[str]
    topics: List[str]

class TextStatistics(BaseModel):
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_sentence_length: float
    avg_word_length: float
    readability_score: float
    language_detected: str

class SummaryResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_text: str
    summary: str
    summary_type: SummaryType
    language_detected: str
    keywords: Optional[KeywordExtraction] = None
    statistics: Optional[TextStatistics] = None
    processing_time: float
    model_used: str
    confidence_score: float
    created_at: datetime = Field(default_factory=datetime.now)

class BatchSummaryRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=10)
    summary_type: SummaryType = SummaryType.ABSTRACTIVE
    summary_length: SummaryLength = SummaryLength.MEDIUM
    language: Language = Language.AUTO
    extract_keywords: bool = True

class BatchSummaryResult(BaseModel):
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    results: List[SummaryResult]
    total_processing_time: float
    success_count: int
    error_count: int

# AI Model Service
class AISummarizerService:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.nlp_models = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_models()
    
    def _load_models(self):
        """Load AI models for summarization and language detection"""
        try:
            # Load summarization models for different languages
            model_configs = {
                "en": {
                    "model": "facebook/bart-large-cnn",
                    "tokenizer": "facebook/bart-large-cnn"
                },
                "multilingual": {
                    "model": "facebook/mbart-large-50-many-to-many-mmt",
                    "tokenizer": "facebook/mbart-large-50-many-to-many-mmt"
                },
                "small": {
                    "model": "t5-small",
                    "tokenizer": "t5-small"
                },
                "base": {
                    "model": "t5-base",
                    "tokenizer": "t5-base"
                }
            }
            
            for model_name, config in model_configs.items():
                try:
                    logger.info(f"Loading model: {model_name}")
                    self.tokenizers[model_name] = AutoTokenizer.from_pretrained(config["tokenizer"])
                    self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained(config["model"])
                    self.models[model_name].to(self.device)
                    self.models[model_name].eval()
                except Exception as e:
                    logger.warning(f"Failed to load model {model_name}: {e}")
            
            # Load language detection model
            try:
                self.language_detector = pipeline(
                    "text-classification",
                    model="papluca/xlm-roberta-base-language-detection"
                )
            except Exception as e:
                logger.warning(f"Failed to load language detector: {e}")
                self.language_detector = None
            
            # Load spaCy models for NLP tasks
            try:
                self.nlp_models["en"] = spacy.load("en_core_web_sm")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}")
                self.nlp_models["en"] = None
            
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise HTTPException(status_code=500, detail="Failed to load AI models")
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        try:
            # Try using the language detector model first
            if self.language_detector:
                result = self.language_detector(text[:1000])  # Use first 1000 chars
                if result and len(result) > 0:
                    detected_lang = result[0]["label"].lower()
                    # Map model output to our language codes
                    lang_mapping = {
                        "en": "en", "es": "es", "fr": "fr", "de": "de",
                        "it": "it", "pt": "pt", "ru": "ru", "zh": "zh",
                        "ja": "ja", "ko": "ko", "ar": "ar", "hi": "hi"
                    }
                    return lang_mapping.get(detected_lang, "en")
            
            # Fallback to langdetect library
            detected = detect(text)
            return detected
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en"  # Default to English
    
    def summarize_text(self, text: str, summary_type: SummaryType, 
                      summary_length: SummaryLength, max_length: Optional[int] = None,
                      min_length: Optional[int] = None, language: str = "en") -> Dict[str, Any]:
        """Summarize text using AI models"""
        try:
            # Select appropriate model based on language and type
            model_name = self._select_model(language, summary_type)
            
            if model_name not in self.models:
                model_name = "small"  # Fallback to small model
            
            tokenizer = self.tokenizers[model_name]
            model = self.models[model_name]
            
            # Set length parameters
            if summary_length == SummaryLength.SHORT:
                max_len = max_length or 50
                min_len = min_length or 10
            elif summary_length == SummaryLength.MEDIUM:
                max_len = max_length or 150
                min_len = min_length or 30
            elif summary_length == SummaryLength.LONG:
                max_len = max_length or 300
                min_len = min_length or 50
            else:  # CUSTOM
                max_len = max_length or 150
                min_len = min_length or 30
            
            # Prepare input based on model type
            if "t5" in model_name.lower():
                # T5 models need "summarize:" prefix
                input_text = f"summarize: {text}"
            elif "bart" in model_name.lower():
                # BART models work with raw text
                input_text = text
            else:
                input_text = text
            
            # Tokenize input
            inputs = tokenizer(
                input_text,
                max_length=1024,
                truncation=True,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            # Generate summary
            with torch.no_grad():
                summary_ids = model.generate(
                    inputs["input_ids"],
                    max_length=max_len,
                    min_length=min_len,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=False
                )
            
            # Decode summary
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            # Post-process based on summary type
            if summary_type == SummaryType.BULLET_POINTS:
                summary = self._convert_to_bullet_points(summary, bullet_points_count=5)
            elif summary_type == SummaryType.HEADLINE:
                summary = self._extract_headline(summary)
            elif summary_type == SummaryType.KEY_POINTS:
                summary = self._extract_key_points(summary)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(text, summary, model)
            
            return {
                "summary": summary,
                "model_used": model_name,
                "confidence_score": confidence
            }
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            # Fallback to extractive summarization
            return self._extractive_summarization(text, summary_type, summary_length)
    
    def _select_model(self, language: str, summary_type: SummaryType) -> str:
        """Select the best model for the given language and task"""
        if language != "en" and "multilingual" in self.models:
            return "multilingual"
        elif summary_type == SummaryType.HEADLINE:
            return "small"  # Use smaller model for headlines
        elif "base" in self.models:
            return "base"
        elif "small" in self.models:
            return "small"
        else:
            return list(self.models.keys())[0] if self.models else "small"
    
    def _convert_to_bullet_points(self, text: str, bullet_points_count: int = 5) -> str:
        """Convert text to bullet points"""
        sentences = sent_tokenize(text)
        
        # Take the most important sentences (simplified approach)
        if len(sentences) <= bullet_points_count:
            bullet_points = sentences
        else:
            # Use TF-IDF to score sentences
            try:
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(sentences)
                sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
                top_indices = sentence_scores.argsort()[-bullet_points_count:][::-1]
                bullet_points = [sentences[i] for i in sorted(top_indices)]
            except:
                # Fallback to first n sentences
                bullet_points = sentences[:bullet_points_count]
        
        # Format as bullet points
        bullet_text = "\n".join([f"• {sent.strip()}" for sent in bullet_points if sent.strip()])
        return bullet_text
    
    def _extract_headline(self, text: str) -> str:
        """Extract a single headline from text"""
        sentences = sent_tokenize(text)
        if sentences:
            # Return the first sentence as headline
            return sentences[0].strip()
        return text[:100] + "..." if len(text) > 100 else text
    
    def _extract_key_points(self, text: str) -> str:
        """Extract key points from text"""
        # This is a simplified implementation
        sentences = sent_tokenize(text)
        
        # Filter for sentences that seem important (contain keywords)
        important_sentences = []
        keywords = ["important", "key", "main", "primary", "essential", "crucial", "significant"]
        
        for sent in sentences:
            if any(keyword.lower() in sent.lower() for keyword in keywords):
                important_sentences.append(sent)
        
        # If no keyword sentences found, use first few sentences
        if not important_sentences:
            important_sentences = sentences[:3]
        
        return " ".join(important_sentences)
    
    def _calculate_confidence(self, original_text: str, summary: str, model) -> float:
        """Calculate confidence score for the summary"""
        try:
            # Simple confidence calculation based on length ratio and model
            original_length = len(original_text.split())
            summary_length = len(summary.split())
            length_ratio = summary_length / original_length if original_length > 0 else 0
            
            # Ideal length ratio for summaries is around 0.1-0.3
            if 0.1 <= length_ratio <= 0.3:
                length_score = 1.0
            elif 0.05 <= length_ratio <= 0.5:
                length_score = 0.8
            else:
                length_score = 0.6
            
            # Model-based confidence (simplified)
            model_score = 0.9 if "large" in str(model) else 0.8
            
            # Combined confidence
            confidence = (length_score * 0.4) + (model_score * 0.6)
            return min(confidence, 0.95)  # Cap at 95%
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.75  # Default confidence
    
    def _extractive_summarization(self, text: str, summary_type: SummaryType, 
                                summary_length: SummaryLength) -> Dict[str, Any]:
        """Fallback extractive summarization"""
        try:
            sentences = sent_tokenize(text)
            
            if not sentences:
                return {
                    "summary": "Unable to generate summary.",
                    "model_used": "extractive_fallback",
                    "confidence_score": 0.5
                }
            
            # Calculate sentence scores using TF-IDF
            try:
                vectorizer = TfidfVectorizer(stop_words='english')
                tfidf_matrix = vectorizer.fit_transform(sentences)
                sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
            except:
                # Fallback to sentence length scoring
                sentence_scores = np.array([len(sent.split()) for sent in sentences])
            
            # Select top sentences based on length requirement
            if summary_length == SummaryLength.SHORT:
                num_sentences = 1
            elif summary_length == SummaryLength.MEDIUM:
                num_sentences = 3
            elif summary_length == SummaryLength.LONG:
                num_sentences = 5
            else:
                num_sentences = 3
            
            num_sentences = min(num_sentences, len(sentences))
            top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
            selected_sentences = [sentences[i] for i in sorted(top_indices)]
            
            # Format based on type
            if summary_type == SummaryType.BULLET_POINTS:
                summary = "\n".join([f"• {sent.strip()}" for sent in selected_sentences])
            else:
                summary = " ".join(selected_sentences)
            
            return {
                "summary": summary,
                "model_used": "extractive_fallback",
                "confidence_score": 0.7
            }
            
        except Exception as e:
            logger.error(f"Extractive summarization failed: {e}")
            return {
                "summary": text[:200] + "..." if len(text) > 200 else text,
                "model_used": "basic_fallback",
                "confidence_score": 0.5
            }
    
    def extract_keywords(self, text: str, keyword_count: int = 10, language: str = "en") -> KeywordExtraction:
        """Extract keywords, key phrases, and entities from text"""
        try:
            # Extract keywords using TF-IDF
            keywords = self._extract_tfidf_keywords(text, keyword_count)
            
            # Extract key phrases (n-grams)
            key_phrases = self._extract_key_phrases(text, keyword_count // 2)
            
            # Extract named entities
            entities = self._extract_entities(text, language)
            
            # Extract topics (simplified)
            topics = self._extract_topics(text, keyword_count // 2)
            
            return KeywordExtraction(
                keywords=keywords,
                key_phrases=key_phrases,
                entities=entities,
                topics=topics
            )
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return KeywordExtraction(
                keywords=[],
                key_phrases=[],
                entities=[],
                topics=[]
            )
    
    def _extract_tfidf_keywords(self, text: str, keyword_count: int) -> List[str]:
        """Extract keywords using TF-IDF"""
        try:
            # Tokenize and remove stopwords
            words = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            words = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 2]
            
            # Calculate TF-IDF scores
            word_freq = Counter(words)
            total_words = len(words)
            
            # Simple TF-IDF calculation
            tfidf_scores = {}
            for word, freq in word_freq.items():
                tf = freq / total_words
                # Simplified IDF (log of total documents / documents containing word)
                idf = np.log(total_words / freq) if freq > 0 else 0
                tfidf_scores[word] = tf * idf
            
            # Get top keywords
            top_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
            return [word for word, score in top_keywords[:keyword_count]]
            
        except Exception as e:
            logger.warning(f"TF-IDF keyword extraction failed: {e}")
            return []
    
    def _extract_key_phrases(self, text: str, phrase_count: int) -> List[str]:
        """Extract key phrases (n-grams)"""
        try:
            sentences = sent_tokenize(text)
            phrases = []
            
            for sentence in sentences:
                words = word_tokenize(sentence.lower())
                # Extract 2-3 word phrases
                for i in range(len(words) - 1):
                    phrase = f"{words[i]} {words[i+1]}"
                    if len(phrase) > 5:  # Minimum phrase length
                        phrases.append(phrase)
                
                for i in range(len(words) - 2):
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                    if len(phrase) > 7:  # Minimum phrase length
                        phrases.append(phrase)
            
            # Count and get top phrases
            phrase_freq = Counter(phrases)
            top_phrases = [phrase for phrase, freq in phrase_freq.most_common(phrase_count)]
            return top_phrases
            
        except Exception as e:
            logger.warning(f"Key phrase extraction failed: {e}")
            return []
    
    def _extract_entities(self, text: str, language: str) -> List[str]:
        """Extract named entities"""
        try:
            if language == "en" and self.nlp_models.get("en"):
                # Use spaCy for entity extraction
                doc = self.nlp_models["en"](text)
                entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
                return list(set(entities))  # Remove duplicates
            else:
                # Fallback to NLTK
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                chunks = ne_chunk(pos_tags)
                
                entities = []
                for chunk in chunks:
                    if hasattr(chunk, 'label'):
                        entity = " ".join([token for token, pos in chunk.leaves()])
                        entities.append(entity)
                
                return list(set(entities))
                
        except Exception as e:
            logger.warning(f"Entity extraction failed: {e}")
            return []
    
    def _extract_topics(self, text: str, topic_count: int) -> List[str]:
        """Extract topics (simplified approach)"""
        try:
            # This is a simplified topic extraction
            # In a real implementation, you might use LDA or other topic modeling
            
            # Get frequent words that might represent topics
            words = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            content_words = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 3]
            
            word_freq = Counter(content_words)
            topics = [word for word, freq in word_freq.most_common(topic_count)]
            
            return topics
            
        except Exception as e:
            logger.warning(f"Topic extraction failed: {e}")
            return []
    
    def calculate_text_statistics(self, text: str, language: str = "en") -> TextStatistics:
        """Calculate various text statistics"""
        try:
            # Basic counts
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            word_count = len([w for w in words if w.isalpha()])
            sentence_count = len(sentences)
            paragraph_count = len(paragraphs)
            
            # Average lengths
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            avg_word_length = sum(len(w) for w in words if w.isalpha()) / word_count if word_count > 0 else 0
            
            # Readability score (simplified Flesch Reading Ease)
            if sentence_count > 0:
                avg_sentence_length_words = word_count / sentence_count
                syllable_count = sum(self._count_syllables(w) for w in words if w.isalpha())
                avg_syllables_per_word = syllable_count / word_count if word_count > 0 else 0
                
                # Flesch Reading Ease formula
                readability_score = 206.835 - (1.015 * avg_sentence_length_words) - (84.6 * avg_syllables_per_word)
                readability_score = max(0, min(100, readability_score))  # Clamp between 0-100
            else:
                readability_score = 0
            
            return TextStatistics(
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                avg_sentence_length=avg_sentence_length,
                avg_word_length=avg_word_length,
                readability_score=readability_score,
                language_detected=language
            )
            
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return TextStatistics(
                word_count=0,
                sentence_count=0,
                paragraph_count=0,
                avg_sentence_length=0,
                avg_word_length=0,
                readability_score=0,
                language_detected=language
            )
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        vowels = "aeiouy"
        word = word.lower()
        syllable_count = 0
        prev_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_was_vowel:
                    syllable_count += 1
                prev_char_was_vowel = True
            else:
                prev_char_was_vowel = False
        
        # Adjust for silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)

# Initialize AI service
ai_service = AISummarizerService()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to AI Text Summarizer API", "version": "1.0.0"}

@app.post("/summarize", response_model=SummaryResult)
async def summarize_text(request: TextSummaryRequest):
    """Summarize text using AI models"""
    import time
    start_time = time.time()
    
    try:
        # Detect language if auto-detect is requested
        if request.language == Language.AUTO:
            detected_language = ai_service.detect_language(request.text)
        else:
            detected_language = request.language.value
        
        # Generate summary
        summary_result = ai_service.summarize_text(
            text=request.text,
            summary_type=request.summary_type,
            summary_length=request.summary_length,
            max_length=request.max_length,
            min_length=request.min_length,
            language=detected_language
        )
        
        # Extract keywords if requested
        keywords = None
        if request.extract_keywords:
            keywords = ai_service.extract_keywords(
                text=request.text,
                keyword_count=request.keyword_count,
                language=detected_language
            )
        
        # Calculate statistics if requested
        statistics = None
        if request.include_statistics:
            statistics = ai_service.calculate_text_statistics(
                text=request.text,
                language=detected_language
            )
        
        processing_time = time.time() - start_time
        
        return SummaryResult(
            original_text=request.text,
            summary=summary_result["summary"],
            summary_type=request.summary_type,
            language_detected=detected_language,
            keywords=keywords,
            statistics=statistics,
            processing_time=processing_time,
            model_used=summary_result["model_used"],
            confidence_score=summary_result["confidence_score"]
        )
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.post("/summarize/file", response_model=SummaryResult)
async def summarize_file(
    file: UploadFile = File(...),
    summary_type: SummaryType = Form(SummaryType.ABSTRACTIVE),
    summary_length: SummaryLength = Form(SummaryLength.MEDIUM),
    extract_keywords: bool = Form(True),
    include_statistics: bool = Form(False)
):
    """Summarize text from uploaded file"""
    try:
        # Read file content
        content = await file.read()
        
        # Try to decode as text
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = content.decode('latin-1')
            except:
                raise HTTPException(status_code=400, detail="Unable to decode file as text")
        
        # Check file size (limit to 50KB)
        if len(text) > 50000:
            text = text[:50000]  # Truncate if too long
        
        # Create summary request
        request = TextSummaryRequest(
            text=text,
            summary_type=summary_type,
            summary_length=summary_length,
            extract_keywords=extract_keywords,
            include_statistics=include_statistics
        )
        
        return await summarize_text(request)
        
    except Exception as e:
        logger.error(f"File summarization failed: {e}")
        raise HTTPException(status_code=500, detail=f"File summarization failed: {str(e)}")

@app.post("/summarize/batch", response_model=BatchSummaryResult)
async def summarize_batch(request: BatchSummaryRequest):
    """Summarize multiple texts in batch"""
    import time
    start_time = time.time()
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, text in enumerate(request.texts):
        try:
            # Create individual request
            individual_request = TextSummaryRequest(
                text=text,
                summary_type=request.summary_type,
                summary_length=request.summary_length,
                language=request.language,
                extract_keywords=request.extract_keywords
            )
            
            # Process summary
            result = await summarize_text(individual_request)
            results.append(result)
            success_count += 1
            
        except Exception as e:
            logger.error(f"Batch item {i} failed: {e}")
            error_count += 1
            # Add error result
            error_result = SummaryResult(
                original_text=text,
                summary=f"Error: {str(e)}",
                summary_type=request.summary_type,
                language_detected="unknown",
                processing_time=0,
                model_used="error",
                confidence_score=0.0
            )
            results.append(error_result)
    
    total_processing_time = time.time() - start_time
    
    return BatchSummaryResult(
        results=results,
        total_processing_time=total_processing_time,
        success_count=success_count,
        error_count=error_count
    )

@app.post("/extract-keywords", response_model=KeywordExtraction)
async def extract_keywords_from_text(
    text: str = Body(...),
    keyword_count: int = Body(10, ge=1, le=50),
    language: Language = Body(Language.AUTO)
):
    """Extract keywords, key phrases, and entities from text"""
    try:
        # Detect language if auto-detect is requested
        if language == Language.AUTO:
            detected_language = ai_service.detect_language(text)
        else:
            detected_language = language.value
        
        # Extract keywords
        keywords = ai_service.extract_keywords(
            text=text,
            keyword_count=keyword_count,
            language=detected_language
        )
        
        return keywords
        
    except Exception as e:
        logger.error(f"Keyword extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")

@app.post("/detect-language")
async def detect_language_endpoint(text: str = Body(...)):
    """Detect the language of the input text"""
    try:
        detected_language = ai_service.detect_language(text)
        
        return {
            "detected_language": detected_language,
            "confidence": 0.85,  # Placeholder confidence
            "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"]
        }
        
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")

@app.post("/analyze-text", response_model=TextStatistics)
async def analyze_text_statistics(
    text: str = Body(...),
    language: Language = Body(Language.AUTO)
):
    """Analyze text statistics and readability"""
    try:
        # Detect language if auto-detect is requested
        if language == Language.AUTO:
            detected_language = ai_service.detect_language(text)
        else:
            detected_language = language.value
        
        # Calculate statistics
        statistics = ai_service.calculate_text_statistics(
            text=text,
            language=detected_language
        )
        
        return statistics
        
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@app.get("/models/status")
async def get_model_status():
    """Get status of loaded AI models"""
    try:
        model_status = {}
        
        for model_name in ai_service.models:
            model_status[model_name] = {
                "loaded": True,
                "device": str(ai_service.device),
                "status": "ready"
            }
        
        return {
            "models": model_status,
            "device": str(ai_service.device),
            "language_detector": ai_service.language_detector is not None,
            "nlp_models": list(ai_service.nlp_models.keys()),
            "total_models_loaded": len(ai_service.models)
        }
        
    except Exception as e:
        logger.error(f"Model status check failed: {e}")
        return {"error": str(e)}

@app.get("/summary-types")
async def get_summary_types():
    """Get available summary types"""
    return {
        "summary_types": [
            {
                "type": "abstractive",
                "name": "Abstractive",
                "description": "Generate new sentences that capture the essence"
            },
            {
                "type": "extractive",
                "name": "Extractive",
                "description": "Extract important sentences from the original text"
            },
            {
                "type": "bullet_points",
                "name": "Bullet Points",
                "description": "Format summary as bullet points"
            },
            {
                "type": "headline",
                "name": "Headline",
                "description": "Generate a single sentence headline"
            },
            {
                "type": "key_points",
                "name": "Key Points",
                "description": "Extract only the most important points"
            }
        ]
    }

@app.get("/languages")
async def get_supported_languages():
    """Get supported languages"""
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "ar", "name": "Arabic"},
            {"code": "hi", "name": "Hindi"},
            {"code": "auto", "name": "Auto-detect"}
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "models_loaded": len(ai_service.models),
        "device": str(ai_service.device),
        "cuda_available": torch.cuda.is_available()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8014)
