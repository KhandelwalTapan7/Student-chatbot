import subprocess
import sys

def install_packages():
    """Install required packages"""
    packages = [
        'Flask==2.3.3',
        'flask-cors==4.0.0',
        'nltk==3.8.1',
        'spacy==3.7.2',
        'scikit-learn==1.3.0',
        'SQLAlchemy==2.0.23',
        'python-dotenv==1.0.0',
        'requests==2.31.0'
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def setup_nltk_data():
    """Download NLTK data"""
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    print("NLTK data downloaded successfully!")

def setup_spacy_model():
    """Download spaCy model"""
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
    print("spaCy model downloaded successfully!")

def create_directory_structure():
    """Create directory structure"""
    import os
    
    directories = [
        'data',
        'static/css',
        'static/js',
        'templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    print("Directory structure created successfully!")

if __name__ == '__main__':
    print("Starting chatbot setup...")
    
    # Update pip first
    print("Updating pip...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    
    # Run setup steps
    install_packages()
    setup_nltk_data()
    setup_spacy_model()
    create_directory_structure()
    
    print("\n" + "="*50)
    print("Setup completed successfully!")
    print("="*50)
    print("\nTo run the chatbot, execute: python app.py")
    print("Then open your browser and go to: http://localhost:5000")