"""
custom_entity_ruler.py
Registers entity patterns for SpaCy using the EntityRuler.
"""

import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler
import json

# Register the component with the SpaCy pipeline
@Language.factory("custom_entity_ruler")
def create_entity_ruler(nlp, name):
    """
    Creates an entity ruler with patterns loaded from a JSON file.

    Args:
        nlp (spacy.language.Language): The SpaCy NLP pipeline.
        name (str): The name of the component (required by SpaCy).
    
    Returns:
        EntityRuler: A ruler component with added patterns.
    """
    ruler = EntityRuler(nlp)

    # Load patterns from a JSON file
    with open("patterns.json", "r") as file:
        patterns = json.load(file)

    ruler.add_patterns(patterns)
    return ruler

def add_entity_ruler(nlp):
    """
    Adds the custom entity ruler to the SpaCy pipeline.
    
    Args:
        nlp (spacy.language.Language): The SpaCy NLP pipeline.
    
    Returns:
        nlp: The modified pipeline with the added custom entity ruler.
    """
    nlp.add_pipe("custom_entity_ruler", before="ner")
    return nlp