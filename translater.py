import spacy
import inflect
import re
import nltk
import unicodedata

from translations import *
from word_forms.word_forms import get_word_forms
from nltk import word_tokenize, pos_tag
from typing import Literal

from rich.console import Console

console = Console()

ACTOR_SUFFIXES = ["er", "or", "ist"]

console.print("[bold bright_green]INFO[/bold bright_green] Loaded translater dependencies!")
console.print("[bold bright_green]INFO[/bold bright_green] Starting [bold]inflect[/bold] engine..")

inflect_engine = inflect.engine()

console.print("[bold bright_green]INFO[/bold bright_green] Loading [bold]SpaCy[/bold] AI model..")

nlp = spacy.load("en_core_web_sm")

wordnet_download_success = False
try:
    nltk.data.find('corpora/wordnet.zip')
    wordnet_download_success = True
    console.print("[bold bright_green]Success![/bold bright_green] Wordnet was found. :)")
except LookupError:
    wordnet_download_success = nltk.download("wordnet")
    if not wordnet_download_success:
        console.print("[bold red]I couldn't download the wordnet AI mdoel... :([/bold red]")
        console.print("The app will still open, but you will have some missing language features.")
        console.input("Press enter to continue.", password=True)

def remove_all_except(text, accents_to_keep = {'\u0302', '\u0303'}):
    """
    Removes all diacritical marks except those in `accents_to_keep`.
    
    :param text: The input string containing diacritical marks.
    :param accents_to_keep: A set of Unicode characters representing the accents to keep.
    :return: The cleaned text with only the specified accents retained.
    """
    # Normalize text to decomposed form (NFD)
    normalized_text = unicodedata.normalize('NFD', text)
    # Keep only base characters and the specified accents
    cleaned_text = ''.join(c for c in normalized_text if unicodedata.category(c) != 'Mn' or c in accents_to_keep)
    return cleaned_text

# Ensure all dictionary values are lists for uniform processing
normalized_translation_dict = {k: ([v] if isinstance(v, str) else v) for k, v in translation_dictionary.items()}
deaccented_translation_dict = {remove_all_except(k): ([v] if isinstance(v, str) else v) for k, v in translation_dictionary.items()}
reverse_mapping = {}
for norm_key in normalized_translation_dict:
    deaccented = remove_all_except(norm_key)
    reverse_mapping[norm_key] = deaccented

def is_actor_form(word: str) -> bool:
    """Check if a word is in actor form based on common English suffixes."""
    return any(word.endswith(suffix) for suffix in ACTOR_SUFFIXES)

def to_actor_form(root: str) -> str:
    """Convert a root word to its actor form following English rules."""
    if root.endswith("e"):
        return root + "r"  # e.g., "bake" → "baker"
    elif re.match(r".*[aeiou][bcdfghjklmnpqrstvwxyz]$", root):
        return root + root[-1] + "er"  # e.g., "run" → "runner"
    else:
        return root + "er"  # Default case

def get_past_tense_verb(verb: str) -> str:
    """
    Returns the past tense form of a verb.
 
    Parameters:
    - verb: str
        The verb for which the past tense is to be determined.
 
    Returns:
    - str:
        The past tense form of the verb.
 
    Examples:
    >>> get_past_tense_verb("run")
    "ran"
 
    >>> get_past_tense_verb("eat")
    "ate"
 
    >>> get_past_tense_verb("write")
    "wrote"
    """
 
    # List of common irregular verbs and their past tense forms
    irregular_verbs = {
        "be": "was",
        "have": "had",
        "do": "did",
        "go": "went",
        "see": "saw",
        "come": "came",
        "give": "gave",
        "take": "took",
        "make": "made",
        "find": "found",
        "know": "knew",
        "think": "thought",
        "say": "said",
        "tell": "told",
        "get": "got",
        "give": "gave",
        "read": "read",
        "wear": "wore",
        "write": "wrote",
        "run": "ran",
        "teach": "taught",
        "swim": "swam",
        "eat": "ate",
        "build": "built",
        "break": "broke",
        "speak": "spoke",
        "sleep": "slept"
        # Add more irregular verbs as needed
    }

    # convert the verb to lowercase
    verb = verb.lower()
 
    # Check if the verb is in the irregular verbs dictionary
    if verb in irregular_verbs:
        return irregular_verbs[verb]
 
    # Check if the verb ends with "e"
    elif verb.endswith("e"):
        return verb + "d"
 
    # Check if the verb ends with a consonant followed by "y"
    elif len(verb) >= 2 and verb[-2] not in "aeiou" and verb[-1] == "y":
        return verb[:-1] + "ied"
 
    # For regular verbs, simply add "ed" to the end
    else:
        return verb + "ed"

def determine_tense(sentence):
    """
    Function to determine the tense of a given sentence.
 
    Parameters:
    - sentence: str
        The input sentence for which the tense needs to be determined.
 
    Returns:
    - str:
        The tense of the sentence: "past", "present", or "future".
    """
 
    sent = list(nlp(sentence).sents)[0]
    if (
        sent.root.tag_ == "VBD" or
        any(w.dep_ == "aux" and w.tag_ == "VBD" for w in sent.root.children)):
        return "past"
 
    # If none of the above conditions are met, the sentence is considered present tense
    return "present"

def from_actor_form(actor, lemma: bool = True):
    """
    Convert an actor form word back to its root.
    """
    # if wordnet is not available we have to make compromises
    if not wordnet_download_success: return actor

    #! I AM AWARE THIS IS COMPLETE AND UTTER DOGSHIT!!!!
    #! THIS IS TURNING AN O(1) OPERATION INTO AN O(n) OPERATION!!!!
    #! I'M CONVERTING A SET TO A LIST, WHICH IS VERY BAD
    #! BUT THIS SET IS SO SMALL I DONT GIVE A SHIT
    #! RAHHHHHH
    forms = list(get_word_forms(actor)["v"])
    try:
        if lemma:
            return nlp(forms[0])[0].lemma_
        return forms[0]
    except IndexError:
        return actor

def get_trailing_punctuation(text, ignore_chars=""):
    # Create a regex pattern that matches punctuation but ignores specified characters
    ignore_chars = re.escape(ignore_chars)  # Escape to handle special characters properly
    pattern = rf'[^\w\s{ignore_chars}]+$'  # Match trailing punctuation excluding ignored ones
    match = re.search(pattern, text)
    
    return match.group(0) if match else ''

def to_gorgus(user_input: str):
    translated = ""
    before_translation = user_input

    # First, sort phrases by length (longer phrases first)
    sorted_phrases = sorted(
        phrase_translations.items(),
        key=lambda item: max(len(p) for p in (item[1] if isinstance(item[1], list) else [item[1]])),
        reverse=True
    )
    
    # Replace phrases with gorgus words      
    for gorgus, english_phrases in sorted_phrases:
        if isinstance(english_phrases, str):
            english_phrases = [english_phrases]  # Ensure it's a list
        for phrase in english_phrases:
            # Use regex to match whole phrase boundaries
            pattern = r'\b' + re.escape(phrase) + r'\b'
            user_input = re.sub(pattern, gorgus, user_input, flags=re.IGNORECASE)

    """for gorgus, english_phrases in phrase_translations.items():
        if isinstance(english_phrases, str):  
            english_phrases = [english_phrases]  # Convert to list for uniformity
        
        for phrase in english_phrases:
            user_input = user_input.replace(phrase, gorgus)"""

    words = user_input.split(" ")

    modified_verbs = {}

    doc = nlp(before_translation)
    for i, token in enumerate(doc):
        if token.text == "EXAGGERATE":
            modified_verbs[token.head.i] = 1
        elif token.text == "GENTLE":
            modified_verbs[token.head.i] = -1

    for i, word in enumerate(words):
        trailing_punctuation = get_trailing_punctuation(word, translation_dictionary["<EXAGGERATED_VERB>"] + translation_dictionary["<GENTLE_VERB>"])
        word = word.translate(str.maketrans('', '', ".?!-,\":()=/\\$"))

        suffix = ""

        if word == "EXAGGERATE" or word == "GENTLE":
            continue

        suffix = modified_verbs.get(i, "")
        if suffix == 1:
            suffix = translation_dictionary["<EXAGGERATED_VERB>"]
        elif suffix == -1:
            suffix = translation_dictionary["<GENTLE_VERB>"]

        if trailing_punctuation.endswith("?"):
            if not word == "lunk":
                suffix += " lunk"
        else:
            suffix += trailing_punctuation

        try:
            plural = inflect_engine.plural(word)
            if not word in ignored_plurals:
                singular = inflect_engine.singular_noun(word)
            else:
                singular = False
            is_plural = singular != False
        except:
            translated += f"{words[i]} "
            continue
        
        word_suffix = ""
        is_actor = False

        is_actor = word not in ignored_actor_nouns and (
            is_actor_form(word) or "erser" in to_actor_form(word)
        )

        if is_actor:
            singular = from_actor_form(word)
            plural = inflect_engine.plural(from_actor_form(plural))

            word_suffix += translation_dictionary["<ACTOR>"]
        
        if is_actor and singular == plural:
            is_plural = True
            singular = to_actor_form(singular)
            plural = inflect_engine.plural(singular)

        if plural in ignored_plurals:
            is_plural = False

        found = False
        for key, value_list in normalized_translation_dict.items():
            value_set = set(value_list)  # Convert to set for faster lookups

            if (singular and singular in value_set) or (word in value_set) or (is_plural and plural in value_set):
                found = True
                plural_prefix = translation_dictionary["<PLURAL>"] if is_plural else ""
                translated += f"{plural_prefix}{key}{word_suffix}{suffix} "
                break

        if not found:
            translated += f"{word}{suffix} "

    # verb modifier words
    translated = replace_word(translated, "really", translation_dictionary["<EXAGGERATED_VERB>"])
    translated = replace_word(translated, "extremely", translation_dictionary["<EXAGGERATED_VERB>"])
    translated = replace_word(translated, "very", translation_dictionary["<EXAGGERATED_VERB>"])
    translated = replace_word(translated, "absolutely", translation_dictionary["<EXAGGERATED_VERB>"])
    translated = replace_word(translated, "kinda", translation_dictionary["<GENTLE_VERB>"])

    return translated

def from_gorgus(user_input: str):
    translated = ""

    user_input = remove_all_except(user_input)

    # Replace phrases with english words      
    for gorgus, english in phrase_translations.items():
        if type(english) == list:
            for phrase in english:
                user_input = user_input.replace(remove_all_except(gorgus), english[0])
        elif type(english) == str:
            user_input = user_input.replace(remove_all_except(gorgus), english)

    words = user_input.split(" ")

    for word in words:
        if word == "lunk":
            translated = translated[:-1] + "? "
            continue

        suffix = ""
        trailing = get_trailing_punctuation(word, translation_dictionary["<EXAGGERATED_VERB>"] + translation_dictionary["<GENTLE_VERB>"])
        suffix += trailing

        word = word.translate(str.maketrans('', '', ".,?!$:()=/\\"))

        plural = False
        actor = False
        if word.startswith(translation_dictionary["<PLURAL>"]):
            word = word.removeprefix(translation_dictionary["<PLURAL>"])
            plural = True

        if word.endswith(translation_dictionary["<ACTOR>"]):
            word = word.removesuffix(translation_dictionary["<ACTOR>"])
            actor = True

        if word.find(translation_dictionary["<EXAGGERATED_VERB>"]) != -1:
            word = word.replace(translation_dictionary["<EXAGGERATED_VERB>"], "")
            translated += "really "
        if word.find(translation_dictionary["<GENTLE_VERB>"]) != -1:
            word = word.replace(translation_dictionary["<GENTLE_VERB>"], "")
            translated += "kinda "

        if word == "ji":
            translated += "ji "
            continue

        #return f'{word, translation_dictionary, translation_dictionary.get(word, " Not found!")}'
        translation = deaccented_translation_dict.get(remove_all_except(word))
    
        if translation:
            final = translation[0]

            if actor:
                final = to_actor_form(final)

            if plural:
                final = inflect_engine.plural(final)

            translated += f"{final}{suffix} "
        else:
            translated += f"{word}{suffix} "
            
    translated = fix_articles(translated, "ji")

    #translated = remove_all_except(translated)

    return translated

def fix_up(translated: str, should_add_accents: bool):
    translated = translated.capitalize().strip()

    if not should_add_accents:
        translated = remove_all_except(translated)

    return translated

def fix_articles(input_string: str, article_word: str):
    words = input_string.split()  # Split the string into words
    result = []

    i = 0
    while i < len(words):
        if words[i].lower() == article_word and i + 1 < len(words):
            # Apply function a to the word after "here"
            result.append(inflect_engine.a(words[i + 1]))
            i += 2  # Skip "here" and the next word as we've processed it
        else:
            # Add the word to the result if it's not part of "here" and the next word
            result.append(words[i])
            i += 1

    return " ".join(result)

def replace_word(input_string: str, word: str, replacement: str, offset: int = 1):
    # Split the input string into words
    words = input_string.split()

    """if offset == None: # we find the closest verb or adjective to our target word and we use that as the offset
        doc = nlp(input_string)
        noun_verb_indicies = []
        for idx, tok in enumerate(doc):
            if tok.pos_ in ["NOUN", "VERB"]:
                noun_verb_indicies.append(idx)

        print(noun_verb_indicies)"""

    # Check if 'very' comes before 'quickly'
    for i in range(len(words) - 1):
        if words[i] == word:
            if words[i+1].lower() == "horge":
                offset = min(offset+1, (len(words)-i)-1)

            trailing = get_trailing_punctuation(words[i+offset])
            len_trailing = len(trailing)

            # Modify 'quickly' by adding '\u0302' and remove 'very'

            if len_trailing > 0:
                words[i + offset] = words[i + offset][:-len(trailing)] + replacement + trailing
            else:
                words[i + offset] = words[i + offset][:] + replacement
            del words[i]  # Remove 'very'

            # Break after the first occurrence is handled
            break

    # Join the words back into a string and return
    return " ".join(words)

def translate(text: str, to: Literal["english", "gorgus"], wordnet_available: bool = True, should_add_accents: bool = True):
    """Translate from or to Gorgus and English!

    Trailing whitespace is not preserved, neither is punctuation.
    """
    text = text.lower().strip()

    if to == "english":
        user_choice = 2
    elif to == "gorgus":
        user_choice = 1
    else:
        raise TypeError("Invalid language conversion! Only options are \"english\" or \"gorgus\".")

    if user_choice == 2: # translate language to english:
            
        translated = from_gorgus(text)

    elif user_choice == 1: # translate english to language      
        
        translated = to_gorgus(text)

    translated = fix_up(translated, should_add_accents)

    return translated


if __name__ == '__main__':
    print("=== translation tests ===\n")

    tests_to_gorgus = [
        "Hi! How are you?",
        "How is the weather?",
        "I love you.",
        "He slept.",
        "What's up?",
        "Do you like to eat?",
        "What is going on?"
    ]

    translated_tests = []

    print("## To Gorgus ##")
    for test in tests_to_gorgus:
        translated = translate(test, 'gorgus')
        translated_tests.append(translated)
        print(f"\"{test}\" : {translated}")

    print("\n## From Gorgus ##")
    for test in translated_tests:
        print(f"\"{test}\" : {translate(test, 'english')}")

    print("\n## Tense Checks ##")
    
    tense_checks = [
        "eat",
        "slept",
        "build",
        "eating",
        "teach",
        "taught",
        "swam",
        "swimming"
    ]

    for check in tense_checks:
        print(f"\"{check}\" : {determine_tense(check)}")