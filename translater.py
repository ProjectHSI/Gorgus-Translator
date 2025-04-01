import spacy
import inflect
import re
import nltk
import unicodedata
import unittest

from translations import *
from word_forms.word_forms import get_word_forms
from nltk.stem import WordNetLemmatizer
from typing import Literal

from rich.console import Console

console = Console()

ACTOR_SUFFIXES = ["er", "or", "ist"]

console.print("[bold bright_green]INFO[/bold bright_green] Loaded translater dependencies!")
console.print("[bold bright_green]INFO[/bold bright_green] Starting [bold]inflect[/bold] engine..")

inflect_engine = inflect.engine()

console.print("[bold bright_green]INFO[/bold bright_green] Loading [bold]SpaCy[/bold] AI model..")

nlp = spacy.load("en_core_web_sm")
lemmatizer = WordNetLemmatizer()

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

def get_word_type(word):
    if word.strip() == "":
        return "UNKOWN"

    # Process the word through the spaCy pipeline
    doc = nlp(word)
    
    # Check if the word is a verb by examining the POS tag
    try:
        return doc[0].pos_
    except IndexError:
        return "UNKOWN"

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

def detect_verb_tense(verb):
    try:
        sent = list(nlp(verb).sents)[0]
    except IndexError:
        return "norm"

    if (
        sent.root.tag_ == "VBD" or
        any(w.dep_ == "aux" and w.tag_ == "VBD" for w in sent.root.children)):
        return "past"
    
    if (
        sent.root.tag_ == "VBG" or
        any(w.dep_ == "aux" and w.tag_ == "VBZ" for w in sent.root.children)):
        return "cont"
    
    return "norm"

def get_past_tense_verb(verb):
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
        "be": "was/were",
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
        # Add more irregular verbs as needed
    }
 
    # Check if the verb is in the irregular verbs dictionary
    if verb in irregular_verbs:
        return irregular_verbs[verb]
 
    # Check if the verb ends with "e"
    elif verb.endswith("e"):
        return verb + "d"
 
    # Check if the verb ends with a consonant followed by "y"
    elif verb[-2] not in "aeiou" and verb[-1] == "y":
        return verb[:-1] + "ied"
 
    # For regular verbs, simply add "ed" to the end
    else:
        return verb + "ed"
    
def convert_to_gerund(verb):
    if verb.endswith("e") and not verb.endswith("ie"):
        return verb[:-1] + "ing"  # Drop 'e' and add 'ing'
    elif verb.endswith("ie"):
        return verb[:-2] + "ying"  # Change 'ie' to 'ying'
    elif len(verb) > 2 and verb[-1] in "aeiou" and len(verb) > 1 and verb[-2] not in "aeiou" and verb[-3] not in "aeiou" and verb[-2] != 'w' and verb[-2] != 'x' and verb[-2] != 'y':
        return verb + verb[-1] + "ing"  # Double the final consonant for CVC pattern
    return verb + "ing"  # Default case for most verbs
    
def get_tense_verb(verb, tense):
    if tense == "past":
        return get_past_tense_verb(verb)
    
    elif tense == "cont":
        return convert_to_gerund(verb)
    
    else:
        return verb

def is_actor_form(word):
    """Check if a word is in actor form based on common English suffixes."""
    return any(word.endswith(suffix) for suffix in ACTOR_SUFFIXES)

def to_actor_form(root):
    """Convert a root word to its actor form following English rules."""
    if root.endswith("e"):
        return root + "r"  # e.g., "bake" → "baker"
    elif re.match(r".*[aeiou][bcdfghjklmnpqrstvwxyz]$", root):
        return root + root[-1] + "er"  # e.g., "run" → "runner"
    else:
        return root + "er"  # Default case

def from_actor_form(actor, lemma = True):
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

def convert_to_base_form(verb):
    return lemmatizer.lemmatize(verb, pos='v')

def to_gorgus(user_input):
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
        if word == "the": # skip "the", there is no equivelant in gorgus
            continue

        trailing_punctuation = get_trailing_punctuation(word, translation_dictionary["<EXAGGERATED_VERB>"] + translation_dictionary["<GENTLE_VERB>"])
        word = word.translate(str.maketrans('', '', "?.!,\":()=/\\$[]"))

        suffix = ""
        punctuation_suffix = ""

        if word == "EXAGGERATE" or word == "GENTLE":
            continue

        suffix = modified_verbs.get(i, "")
        if suffix == 1:
            suffix = translation_dictionary["<EXAGGERATED_VERB>"]
        elif suffix == -1:
            suffix = translation_dictionary["<GENTLE_VERB>"]

        if trailing_punctuation.endswith("?"):
            if word != "lunk":
                punctuation_suffix += " lunk"
        else:
            punctuation_suffix += trailing_punctuation

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

        # we need to figure out what tense the verb is in :DDDDD (this is fucking painful, we also only use this if the word is a verb)
        tense = detect_verb_tense(word)
        word_type = get_word_type(word)
        base_word = convert_to_base_form(word)

        found = False
        for key, value_list in normalized_translation_dict.items():
            value_set = set(value_list)  # Convert to set for faster lookups

            if (word_type != "VERB" and ((singular and singular in value_set) or (word in value_set) or (is_plural and plural in value_set))) or (word_type == "VERB" and base_word in value_set):
                found = True
                plural_prefix = translation_dictionary["<PLURAL>"] if is_plural else ""
                tense_suffix = translation_dictionary.get(f"<{tense.upper()}_TENSE>", "") if word_type == "VERB" else ""

                translated += f"{plural_prefix}{key}{word_suffix}{suffix}{tense_suffix}{punctuation_suffix} "
                break

        if not found:
            translated += f"{word}{suffix}{punctuation_suffix} "

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

        word = word.translate(str.maketrans('', '', ".,?!$:()=/\\[]"))

        plural = False
        actor = False

        tense = "norm"
        for tense_key, tense_value in {translation_dictionary["<CONT_TENSE>"]: "cont", translation_dictionary["<PAST_TENSE>"]: "past"}.items():
            if tense_key in word:
                word = word.replace(tense_key, "")
                tense = tense_value
                break

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

            final = get_tense_verb(final, tense)

            translated += f"{final}{suffix} "
        else:
            translated += f"{word}{suffix} "
            
    translated = fix_articles(translated, "ji")

    #translated = remove_all_except(translated)

    return translated

def fix_up(translated, should_add_accents):
    translated = translated.capitalize().strip()

    if not should_add_accents:
        translated = remove_all_except(translated)

    # capitalise the word "I"
    translated = re.sub(r'\bi\b', 'I', translated)

    # Regex pattern to find words that come after ".", "?", "!", or "lunk"
    translated = re.sub(r'([.?!]|\blunk\b)\s*(\w)', lambda m: m.group(1) + ' ' + m.group(2).upper(), translated, flags=re.IGNORECASE)

    return translated

def fix_articles(input_string, article_word):
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

def replace_word(input_string, word, replacement, offset = 1):
    # Split the input string into words
    words = input_string.split()

    # Check if 'very' comes before 'quickly'
    thingy = 0 # i don't what to call this variable, we use this so that whenever we delete a word, we're still at the correct word or something idfk

    for i in range(len(words) - 1):
        if words[i - thingy] == word and len(words) > i+1 - thingy:
            if words[i+1 - thingy].lower() == "horge":
                offset = min(offset+1, (len(words)-i)-1)

            trailing = get_trailing_punctuation(words[i+offset-thingy])
            len_trailing = len(trailing)

            # Modify 'quickly' by adding '\u0302' and remove 'very'

            if len_trailing > 0:
                words[i + offset - thingy] = words[i + offset - thingy][:-len(trailing)] + replacement + trailing
            else:
                words[i + offset - thingy] = words[i + offset - thingy][:] + replacement
            del words[i - thingy]  # Remove 'very'

            thingy += 1

    # Join the words back into a string and return
    return " ".join(words)

def translate(text, to: Literal["english", "gorgus"], wordnet_available = True, should_add_accents = True):
    """Translate from or to Gorgus and English!

    Trailing whitespace is not preserved, neither is punctuation.
    """
    if text.strip() == "":
        return ""

    text = text.lower().strip()
    text = text.replace("\n", " ")

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


class TranslationTester(unittest.TestCase):
    def test_to_gorgus(self):
        # key = english, value = expected gorgus translation
        tests_to_gorgus = {
            "Very cool! Very good. :)": "Klû! Dagungâ. :)",
            "Hi! How are you?": "Dink! Dup pritter-ok lunk",
            "How is the weather?": "Dup gorse weather lunk",
            "I love you.": "H'aggo googrung.",
            "He slept.": "Nåck eep-ra.",
            "What's up?": "Dup pritter-ok lunk",
            "Do you like to eat?": "Gè'googrung jeek tå ćhong̱le̱ lunk",
            "What is going on?": "Nergo're pritter-ok hoog lunk"
        }

        # go through each test
        for english, gorgus in tests_to_gorgus.items():
            self.assertEqual(translate(english, "gorgus"), gorgus, "Translation from English to Gorgus does not match!")

    def test_from_gorgus(self):
        # key = gorgus, value = expected english translation
        tests_from_gorgus = {
            "Dink, dup pritter-ok lunk": "Hello, how are you going?",
            "Henġer agger ik-fren!": "I love dogs!",
            "Glonk ćhong̱le̱-ok migtir omnom!": "Stop eating all food!",
            "Googrung kiff!": "You smell!",
            "Minġer goob'rung ji dagsâ dublub. :)": "I hope you have a really nice day. :)",
            "Jid shrerack, henġer huffer clor'ge dagsa.": "That person, I believe they're nice."
        }

        # go through each test
        for gorgus, english in tests_from_gorgus.items():
            self.assertEqual(translate(gorgus, "english"), english, "Translation from Gorgus to English does not match!")

    def test_tense_detection(self):
        # key = verb, value = expected tense
        # norm = normal tense (eat, drink)
        # past = past tense (ate, drank)
        # cont = continuing tense (eating, drinking)

        tense_tests = {
            "eat": "norm",
            "sat": "past",
            "teaching": "cont",
            "speaking": "cont",
            "try": "norm",
            "rented": "past",
            "make": "norm",
            "wanting": "cont"
        }
        for verb, expected_tense in tense_tests.items():
            self.assertEqual(detect_verb_tense(verb), expected_tense, f"Detected verb tense and expected verb tense do not match! ({verb})")


if __name__ == '__main__':
    unittest.main()