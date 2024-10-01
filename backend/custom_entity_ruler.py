import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler
from spacy.matcher import PhraseMatcher
import json
import os

@Language.factory("custom_entity_ruler")
def create_entity_ruler(nlp, name):
    """
    Creates an entity ruler and phrase matcher for multi-word entities using patterns loaded from a JSON file.
    """
    ruler = EntityRuler(nlp)

    # Load patterns from a JSON file and check if they load correctly
    patterns_path = "patterns.json"
    if not os.path.exists(patterns_path):
        print(f"Error: {patterns_path} does not exist!")
    else:
        with open(patterns_path, "r") as file:
            patterns = json.load(file)
            print("Patterns Loaded: ", patterns)  # Debug: Ensure patterns are loaded

    if not patterns:
        print("Error: No patterns loaded from patterns.json!")
    else:
        # Separate single-word patterns (strings) from multi-word ones (lists)
        simple_patterns = [p for p in patterns if isinstance(p['pattern'], str)]
        multi_word_patterns = [p for p in patterns if isinstance(p['pattern'], list)]

        # Add simple patterns to the EntityRuler
        if simple_patterns:
            ruler.add_patterns(simple_patterns)
            print("Added Simple Patterns to EntityRuler")  # Debug: Confirm addition

        # Add PhraseMatcher for multi-word patterns
        matcher = PhraseMatcher(nlp.vocab)
        if multi_word_patterns:
            for entry in multi_word_patterns:
                if isinstance(entry['pattern'], list):
                    try:
                        # Ensure that each token is a dict with a 'LOWER' key
                        phrase_pattern = nlp.make_doc(' '.join([token['LOWER'] for token in entry['pattern'] if 'LOWER' in token]))
                        matcher.add(entry['label'], [phrase_pattern])
                        print(f"Added Multi-word Pattern: {phrase_pattern.text} for Label: {entry['label']}")  # Debug: Check each pattern
                    except KeyError:
                        print(f"Error: Invalid pattern format in {entry['pattern']}")  # Handle missing 'LOWER' key

            # Define a custom function to apply PhraseMatcher
            @Language.component("custom_phrase_matcher")
            def custom_phrase_matcher(doc):
                matches = matcher(doc)
                spans = [doc[start:end] for _, start, end in matches]
                for span in spans:
                    doc.ents += (span,)
                return doc

            # Add the custom phrase matcher to the pipeline before the NER
            nlp.add_pipe("custom_phrase_matcher", before="ner")
        else:
            print("Error: No multi-word patterns were added!")

    return ruler

def add_entity_ruler(nlp):
    """
    Adds the custom entity ruler and phrase matcher to the SpaCy pipeline.
    """
    nlp.add_pipe("custom_entity_ruler", before="ner")
    return nlp
