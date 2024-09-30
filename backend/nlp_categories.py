"""
nlp_categories.py
Handles the categorization of incidents based on recognized entities from SpaCy.
"""

import spacy

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

# Function to categorize incidents based on extracted entities
def categorize_incident(description):
    """
    Categorizes incidents based on extracted entities from the description.
    
    Args:
        description (str): The text description of the incident.
    
    Returns:
        tuple: A category (str) and the extracted entities (list).
    """
    if not isinstance(description, str) or not description:
        return "Unknown", []

    try:
        doc = nlp(description)
        category = "Unknown"
        entities = [(ent.text, ent.label_) for ent in doc.ents] # Extract entities

        # Example categories based on entities recognized by SpaCy
        for ent in doc.ents:
            if ent.label_ == "ORG":
                category = "System Issue"
            elif ent.label_ == "LOC":
                category = "Network Issue"
            elif ent.label_ == "PERSON":
                category = "User Issue"
            elif ent.label_ == "GPE":  # Countries, cities, states
                category = "Location-Specific Issue"
            elif ent.label_ == "DATE":
                category = "Time-Sensitive Issue"
            elif ent.label_ == "PRODUCT":  # Products or software
                category = "Product Issue"
            elif ent.label_ == "EVENT":  # Conferences, natural disasters
                category = "Event-Related Issue"
            elif ent.label_ == "WORK_OF_ART":
                category = "Creative Work Issue"
            elif ent.label_ == "LANGUAGE":
                category = "Language Issue"
            elif ent.label_ == "FAC":  # Buildings, airports, etc.
                category = "Facility Issue"
            elif ent.label_ == "NORP":  # Nationalities or religious/political groups
                category = "Group-Related Issue"
        
        return category, entities
    except Exception as e: 
        print(f"Error processing description: {e}")
        return "unknown", []
    
