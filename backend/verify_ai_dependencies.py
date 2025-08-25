#!/usr/bin/env python3
"""
Verify AI Dependencies Installation
"""

import sys

def check_import(module_name, display_name=None):
    if display_name is None:
        display_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {display_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {display_name} - FAILED: {e}")
        return False

def main():
    print("Checking AI/ML Dependencies for Interstate Cab Booking")
    print("=" * 50)
    
    dependencies = [
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("sklearn", "Scikit-learn"),
        ("langchain", "LangChain Core"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langchain_anthropic", "LangChain Anthropic"),
        ("langchain_community", "LangChain Community"),
        ("spacy", "SpaCy"),
        ("nltk", "NLTK"),
        ("transformers", "Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("chromadb", "ChromaDB"),
        ("torch", "PyTorch"),
        ("tiktoken", "Tiktoken"),
        ("openai", "OpenAI"),
        ("anthropic", "Anthropic"),
        ("google.generativeai", "Google Generative AI"),
        ("huggingface_hub", "Hugging Face Hub"),
    ]
    
    failed = []
    
    for module, name in dependencies:
        if not check_import(module, name):
            failed.append(name)
    
    print("\n" + "=" * 50)
    
    if failed:
        print(f"\n❌ {len(failed)} dependencies failed to import:")
        for dep in failed:
            print(f"  - {dep}")
        print("\nPlease run: ./install_dependencies.sh")
        sys.exit(1)
    else:
        print("\n✅ All AI dependencies are properly installed!")
        
        # Check for spacy model
        print("\nChecking SpaCy language model...")
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            print("✅ SpaCy language model 'en_core_web_sm' is installed")
        except:
            print("❌ SpaCy language model 'en_core_web_sm' is not installed")
            print("   Run: python -m spacy download en_core_web_sm")
        
        # Check for NLTK data
        print("\nChecking NLTK data...")
        try:
            import nltk
            nltk.data.find('tokenizers/punkt')
            print("✅ NLTK punkt tokenizer is installed")
        except:
            print("❌ NLTK data is not complete")
            print("   Run: python -c \"import nltk; nltk.download('punkt')\"")

if __name__ == "__main__":
    main()
