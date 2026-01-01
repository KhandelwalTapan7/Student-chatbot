import numpy as np
import json
import re
import random
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy
import pickle

class ChatbotModel:
    def __init__(self, model_path='chatbot_model.pkl', retrain=False):
        """
        Initialize the chatbot model
        
        Args:
            model_path: Path to save/load trained model
            retrain: Whether to retrain the model
        """
        self.model_path = model_path
        self.nlp = None
        self.stop_words = None
        self.model = None
        self.vectorizer = None
        self.training_data = {}
        self.responses = {}
        
        # Initialize NLP components with error handling
        self.init_nlp()
        
        # Load or train model
        if not retrain and os.path.exists(model_path):
            self.load_model()
        else:
            self.load_training_data()
            self.train_model()
            self.save_model()
        
        print("Chatbot model initialized successfully!")
    
    def init_nlp(self):
        """Initialize NLP components with proper error handling"""
        try:
            # Download required NLTK data
            required_nltk_data = ['punkt', 'punkt_tab', 'stopwords', 'wordnet']
            
            for data in required_nltk_data:
                try:
                    nltk.data.find(f'tokenizers/{data}')
                except LookupError:
                    print(f"Downloading NLTK data: {data}")
                    nltk.download(data, quiet=True)
            
            # Initialize stopwords
            self.stop_words = set(stopwords.words('english'))
            
        except Exception as e:
            print(f"Warning: NLTK initialization error: {e}")
            # Fallback to a simple stopwords list
            self.stop_words = set(['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
        # Initialize spaCy
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            print("Downloading spaCy model...")
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
                self.nlp = spacy.load('en_core_web_sm')
            except:
                print("Warning: Could not load spaCy model. Entity recognition disabled.")
                self.nlp = None
    
    def load_training_data(self):
        """Load training data from JSON files or use defaults"""
        # Try to load from file
        if os.path.exists('data/training_data.json'):
            with open('data/training_data.json', 'r', encoding='utf-8') as f:
                self.training_data = json.load(f)
            print(f"Loaded training data from file with {len(self.training_data)} intents")
        else:
            self.training_data = self.get_default_training_data()
            print(f"Using default training data with {len(self.training_data)} intents")
        
        # Try to load responses from file
        if os.path.exists('data/responses.json'):
            with open('data/responses.json', 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
            print(f"Loaded responses from file with {len(self.responses)} intents")
        else:
            self.responses = self.get_default_responses()
            print(f"Using default responses with {len(self.responses)} intents")
    
    def get_default_training_data(self):
        """Default training data if file not found"""
        return {
            "greeting": {
                "patterns": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "hello there", "hi there"],
                "responses": ["Hello! How can I help you today?", "Hi there! What can I assist you with?"]
            },
            "attendance": {
                "patterns": ["attendance", "present percentage", "attendance record", "how many days present", "attendance policy", "check attendance"],
                "responses": ["Your attendance is available on the student portal.", "Attendance records are updated weekly."]
            },
            "exam_schedule": {
                "patterns": ["exam dates", "when are exams", "exam schedule", "final exam timetable", "mid term exams", "exam time", "exam timing"],
                "responses": ["Exam schedules are published one month before exams.", "Check the university website for exam dates."]
            },
            "fees": {
                "patterns": ["fee payment", "tuition fees", "semester fees", "payment deadline", "how to pay fees", "fee structure", "pay fees"],
                "responses": ["Fee deadlines are mentioned in the academic calendar.", "You can pay fees through the online portal."]
            },
            "courses": {
                "patterns": ["available courses", "course registration", "elective subjects", "course syllabus", "register for courses", "subjects", "courses offered"],
                "responses": ["Course catalogs are available on the department website.", "Register for courses through the student portal."]
            },
            "library": {
                "patterns": ["library timings", "library hours", "borrow books", "library card", "library rules", "book return", "library facilities"],
                "responses": ["Library is open from 8 AM to 8 PM on weekdays.", "You need a student ID card to borrow books."]
            },
            "hostel": {
                "patterns": ["hostel admission", "hostel fees", "hostel facilities", "room allotment", "hostel rules", "hostel food", "hostel accommodation"],
                "responses": ["Hostel admission forms are available at the hostel office.", "Hostel fees vary depending on room type."]
            },
            "goodbye": {
                "patterns": ["bye", "goodbye", "see you", "see you later", "take care", "thanks bye"],
                "responses": ["Goodbye! Have a great day!", "See you later! Feel free to ask if you have more questions."]
            },
            "thanks": {
                "patterns": ["thank you", "thanks", "thank you so much", "thanks a lot", "appreciate it"],
                "responses": ["You're welcome!", "Happy to help!", "Glad I could assist you!"]
            },
            "unknown": {
                "patterns": [],
                "responses": ["I'm not sure I understand. Could you rephrase that?", "I don't have information about that yet."]
            }
        }
    
    def get_default_responses(self):
        """Default responses if file not found"""
        return {
            "greeting": [
                "Hello! Welcome to Student Query Assistant. How can I help you today?",
                "Hi there! I'm here to assist with your academic queries. What would you like to know?",
                "Welcome! I can help you with exam schedules, attendance, fees, courses, and more. How can I assist you?"
            ],
            "attendance": [
                "Attendance records can be viewed on the student portal under 'My Attendance' section.",
                "You need minimum 75% attendance to appear for exams. Check your current percentage on the portal.",
                "Attendance is updated every Friday by your class coordinator. Contact them if there are discrepancies."
            ],
            "exam_schedule": [
                "The exam schedule for this semester will be published on December 1st on the university website.",
                "Mid-term exams start next week. Check your department notice board for the detailed schedule.",
                "Final exams are usually held in May and December. The exact dates will be announced one month prior."
            ],
            "fees": [
                "The last date for fee payment is 15th of every month. Late fees apply after the deadline.",
                "You can pay fees online through the university payment gateway using credit/debit cards or net banking.",
                "Fee structure is available in the academic handbook. Contact accounts office for detailed breakdown."
            ],
            "courses": [
                "Course registration for next semester opens on January 10th and closes on January 20th.",
                "The complete course list and syllabus are available in the academic handbook on the department website.",
                "You can choose elective subjects during the registration period. Consult your academic advisor for guidance."
            ],
            "library": [
                "Library timings: Monday to Friday - 8 AM to 8 PM, Saturday - 9 AM to 5 PM, Sunday - Closed",
                "You can borrow up to 5 books for 15 days with your student ID card.",
                "Online library resources are available 24/7 through the library portal with your student login."
            ],
            "hostel": [
                "Hostel admission for new students starts from July 1st. Forms are available at the hostel office.",
                "Hostel fees: Single room - ₹50,000/semester, Double sharing - ₹35,000/semester.",
                "Hostel facilities include Wi-Fi, laundry, gym, and 24/7 security. Visit hostel office for details."
            ],
            "goodbye": [
                "Goodbye! Have a great day!",
                "See you later! Feel free to ask if you have more questions.",
                "Take care! Don't hesitate to reach out if you need help."
            ],
            "thanks": [
                "You're welcome!",
                "Happy to help!",
                "Glad I could assist you!",
                "Anytime! Let me know if you need anything else."
            ],
            "unknown": [
                "I'm not sure I understand. Could you rephrase your question?",
                "I don't have information about that yet. Please contact the administration office.",
                "That's an interesting question. Let me connect you with a human administrator.",
                "I'm still learning. Could you try asking in a different way?",
                "Sorry, I couldn't understand that. Can you please rephrase or ask something else?"
            ]
        }
    
    def simple_tokenize(self, text):
        """Simple tokenization without NLTK dependency"""
        # Remove special characters and convert to lowercase
        text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        # Split by whitespace and filter out empty strings
        tokens = [word.strip() for word in text.split() if word.strip()]
        # Remove stopwords if available
        if self.stop_words:
            tokens = [word for word in tokens if word not in self.stop_words]
        # Remove very short words
        tokens = [word for word in tokens if len(word) > 2]
        return tokens
    
    def preprocess_text(self, text):
        """
        Preprocess text for model training/prediction
        
        Args:
            text: Input text string
            
        Returns:
            Preprocessed text string
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters, digits, and extra spaces
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        try:
            # Try using NLTK tokenizer
            tokens = word_tokenize(text)
        except:
            # Fallback to simple tokenization
            tokens = self.simple_tokenize(text)
        
        # Remove stopwords
        if self.stop_words:
            tokens = [word for word in tokens if word not in self.stop_words]
        
        # Remove very short words
        tokens = [word for word in tokens if len(word) > 2]
        
        return ' '.join(tokens)
    
    def prepare_training_data(self):
        """Prepare training data for model"""
        X = []  # Features
        y = []  # Labels
        
        for intent, data in self.training_data.items():
            for pattern in data['patterns']:
                processed_pattern = self.preprocess_text(pattern)
                if processed_pattern:  # Only add non-empty patterns
                    X.append(processed_pattern)
                    y.append(intent)
        
        # Add fallback patterns for unknown intent
        fallback_patterns = [
            "random question",
            "what is the meaning of life",
            "tell me a joke",
            "who are you",
            "what can you do",
            "help me with something else"
        ]
        
        for pattern in fallback_patterns:
            processed = self.preprocess_text(pattern)
            if processed:
                X.append(processed)
                y.append("unknown")
        
        print(f"Prepared {len(X)} training samples for {len(set(y))} intents")
        return X, y
    
    def train_model(self):
        """Train the chatbot model"""
        print("Training chatbot model...")
        
        # Prepare training data
        X, y = self.prepare_training_data()
        
        if len(X) == 0:
            print("Error: No training data available!")
            return
        
        # Create and train the model pipeline
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1500,
                ngram_range=(1, 2),  # Reduced from (1,3) to prevent memory issues
                stop_words='english',
                min_df=1,
                max_df=0.9
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Train the model
        self.model.fit(X, y)
        
        # Test model accuracy
        train_predictions = self.model.predict(X)
        accuracy = np.mean(train_predictions == y)
        print(f"Model training completed! Training accuracy: {accuracy:.2%}")
        
        # Store the vectorizer for later use
        self.vectorizer = self.model.named_steps['tfidf']
    
    def save_model(self):
        """Save trained model to file"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'training_data': self.training_data,
                    'responses': self.responses,
                    'vectorizer': self.vectorizer
                }, f)
            print(f"Model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self):
        """Load trained model from file"""
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.training_data = data['training_data']
                self.responses = data['responses']
                self.vectorizer = data['vectorizer']
            print(f"Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}. Retraining...")
            self.load_training_data()
            self.train_model()
            self.save_model()
    
    def extract_entities(self, text):
        """
        Extract named entities from text using spaCy
        
        Args:
            text: Input text
            
        Returns:
            List of entities
        """
        entities = []
        
        if self.nlp and text:
            try:
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
            except Exception as e:
                print(f"Error extracting entities: {e}")
        
        return entities
    
    def process_query(self, query):
        """
        Process a user query and generate response
        
        Args:
            query: User input text
            
        Returns:
            (intent, confidence, response, entities)
        """
        if not query or not isinstance(query, str) or query.strip() == '':
            return 'unknown', 0.0, "Please enter a valid query.", []
        
        # Preprocess query
        processed_query = self.preprocess_text(query)
        
        if not processed_query or len(processed_query.split()) == 0:
            return 'unknown', 0.0, "I didn't understand that. Could you please rephrase?", []
        
        # Extract entities
        entities = self.extract_entities(query)
        
        # Predict intent using model
        try:
            if self.model is None:
                raise ValueError("Model not initialized")
                
            intent = self.model.predict([processed_query])[0]
            confidence = max(self.model.predict_proba([processed_query])[0])
            
        except Exception as e:
            print(f"Prediction error: {e}")
            intent = 'unknown'
            confidence = 0.0
        
        # Generate response
        response = self.generate_response(intent, entities, query)
        
        return intent, confidence, response, entities
    
    def generate_response(self, intent, entities, original_query):
        """
        Generate response based on intent and entities
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            original_query: Original user query
            
        Returns:
            Response text
        """
        # Check if intent exists in responses
        if intent in self.responses and self.responses[intent]:
            responses_list = self.responses[intent]
            
            # Return random response from the list
            return random.choice(responses_list)
        
        # Fallback to unknown intent
        return random.choice(self.responses.get('unknown', ["I'm not sure how to respond to that."]))
    
    def get_suggested_questions(self, intent=None, count=5):
        """
        Get suggested questions based on intent
        
        Args:
            intent: Specific intent or None for random
            count: Number of suggestions
            
        Returns:
            List of suggested questions
        """
        suggestions = []
        
        if intent and intent in self.training_data:
            # Get patterns for specific intent
            patterns = self.training_data[intent]['patterns']
            if len(patterns) > 0:
                count = min(count, len(patterns))
                suggestions = random.sample(patterns, count)
        else:
            # Get random patterns from all intents
            all_patterns = []
            for intent_data in self.training_data.values():
                all_patterns.extend(intent_data['patterns'])
            
            if len(all_patterns) > 0:
                count = min(count, len(all_patterns))
                suggestions = random.sample(all_patterns, count)
        
        return suggestions

# Create a setup script to download NLTK data
def setup_nltk():
    """Download required NLTK data"""
    print("=" * 60)
    print("SETTING UP NLTK DATA")
    print("=" * 60)
    
    try:
        import nltk
        
        # List of required NLTK data
        required_data = [
            ('punkt', 'tokenizers/punkt'),
            ('punkt_tab', 'tokenizers/punkt_tab'),
            ('stopwords', 'corpora/stopwords'),
            ('wordnet', 'corpora/wordnet')
        ]
        
        for data_name, data_path in required_data:
            try:
                print(f"\nChecking {data_name}...")
                nltk.data.find(data_path)
                print(f"✓ {data_name} already installed")
            except LookupError:
                print(f"Downloading {data_name}...")
                nltk.download(data_name, quiet=False)
                print(f"✓ Downloaded {data_name}")
        
        print("\n" + "=" * 60)
        print("NLTK SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError setting up NLTK: {e}")
        print("\nYou can manually download NLTK data by running:")
        print("python -c \"import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')\"")

# Test the chatbot model
if __name__ == '__main__':
    print("=" * 60)
    print("TESTING CHATBOT MODEL")
    print("=" * 60)
    
    # Setup NLTK data first
    setup_nltk()
    
    # Create chatbot instance
    print("\nCreating chatbot instance...")
    chatbot = ChatbotModel(retrain=True)
    
    # Test queries
    test_queries = [
        "hello",
        "hi there",
        "when is the exam?",
        "exam schedule please",
        "how to check my attendance?",
        "attendance percentage",
        "fee payment deadline",
        "how to pay semester fees?",
        "course registration process",
        "available courses for next semester",
        "library timings",
        "hostel admission",
        "thank you",
        "bye",
        "what is the weather today?",  # Should fall to unknown
        "tell me a joke"  # Should fall to unknown
    ]
    
    print("\nTesting queries:")
    print("-" * 60)
    
    for query in test_queries:
        intent, confidence, response, entities = chatbot.process_query(query)
        
        print(f"\nQuery: {query}")
        print(f"Intent: {intent} (Confidence: {confidence:.2%})")
        print(f"Response: {response}")
        if entities:
            print(f"Entities: {entities}")
        print("-" * 40)
    
    # Test suggested questions
    print("\nSuggested questions:")
    print("-" * 60)
    suggestions = chatbot.get_suggested_questions(count=8)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
    
    print("\n" + "=" * 60)
    print("CHATBOT MODEL TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)