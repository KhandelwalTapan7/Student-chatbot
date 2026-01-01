#!/usr/bin/env python3
"""
Script to download required NLTK data for the chatbot
"""

import nltk
import sys

def download_nltk_data():
    """Download all required NLTK data"""
    print("=" * 60)
    print("DOWNLOADING NLTK DATA FOR STUDENT CHATBOT")
    print("=" * 60)
    
    # List of required NLTK data packages
    required_packages = [
        'punkt',        # Tokenizer
        'punkt_tab',    # Tokenizer tables
        'stopwords',    # Stopwords corpus
        'wordnet',      # WordNet lexical database
        'averaged_perceptron_tagger',  # POS tagger
        'maxent_ne_chunker',  # Named entity chunker
        'words'         # Word list
    ]
    
    for package in required_packages:
        try:
            print(f"\nChecking {package}...")
            
            # Check if already downloaded
            try:
                if package == 'punkt':
                    nltk.data.find('tokenizers/punkt')
                elif package == 'punkt_tab':
                    nltk.data.find('tokenizers/punkt_tab')
                elif package == 'stopwords':
                    nltk.data.find('corpora/stopwords')
                elif package == 'wordnet':
                    nltk.data.find('corpora/wordnet')
                elif package == 'averaged_perceptron_tagger':
                    nltk.data.find('taggers/averaged_perceptron_tagger')
                elif package == 'maxent_ne_chunker':
                    nltk.data.find('chunkers/maxent_ne_chunker')
                elif package == 'words':
                    nltk.data.find('corpora/words')
                    
                print(f"✓ {package} already installed")
                continue
            except LookupError:
                pass
            
            # Download the package
            print(f"Downloading {package}...")
            nltk.download(package, quiet=False)
            print(f"✓ Downloaded {package}")
            
        except Exception as e:
            print(f"✗ Error downloading {package}: {e}")
    
    print("\n" + "=" * 60)
    print("NLTK DATA DOWNLOAD COMPLETED!")
    print("=" * 60)
    print("\nYou can now run the chatbot with:")
    print("python app.py")

if __name__ == '__main__':
    try:
        download_nltk_data()
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)