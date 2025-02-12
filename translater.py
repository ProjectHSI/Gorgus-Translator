import string
import spacy
import inflect
import re

from translations import *
from swap import swap_verbs_and_adverbs
from word_forms.word_forms import get_word_forms
from typing import Literal

ACTOR_SUFFIXES = ["er", "or", "ist"]

inflect_engine = inflect.engine()
nlp = spacy.load("en_core_web_sm")


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


def from_actor_form(actor, lemma: bool = True):
    """
    Convert an actor form word back to its root.
    """
    #! I AM AWARE THIS IS COMPLETE AND UTTER DOGSHIT!!!!
    #! THIS IS TURNING AN O(1) OPERATION INTO AN O(n) OPERATION!!!!
    #! BUT THIS SET IS SO SMALL I DONT GIVE A SHIT
    #! RAHHHHHH
    forms = list(get_word_forms(actor)["v"])
    try:
        if lemma:
            return nlp(forms[0])[0].lemma_
        return forms[0]
    except IndexError:
        return actor

def get_trailing_punctuation(text):
    # Match any punctuation at the end of the string
    match = re.search(r'[\W_]+$', text)
    if match:
        return match.group(0)
    return ''

def to_gorgus(user_input: str):
    translated = ""

    # Remove punctuation
    user_input = user_input.translate(str.maketrans('', '', ",")).strip()

    # Swap verbs and adverbs if needed
    user_input = swap_verbs_and_adverbs(user_input)
    
    # Replace phrases with gorgus words      
    for gorgus, english in phrase_translations.items():

        if type(english) == list:
            for phrase in english:
                user_input = user_input.replace(phrase, gorgus)
        elif type(english) == str:
                user_input = user_input.replace(english, gorgus)

    words = user_input.split(" ")
    before_translation = user_input

    modified_verbs = {}

    doc = nlp(before_translation)
    for i, token in enumerate(doc):
        #print(token.pos_, token.text)
        #print(token.nbor().pos_, token.nbor().text)
        if token.text == "EXAGGERATE":
            modified_verbs[token.head.i] = 1
        elif token.text == "GENTLE":
            modified_verbs[token.head.i] = -1

    for i, word in enumerate(words):
        token_word = nlp(word)[0]
        trailing_punctuation = get_trailing_punctuation(word)

        word = word.translate(str.maketrans('', '', string.punctuation))

        suffix = ""

        if word == "EXAGGERATE" or word == "GENTLE":
            continue

        try:
            suffix = modified_verbs.get(i)


            if suffix == None:
                suffix = ""

            if suffix == 1:
                suffix = translation_dictionary["<EXAGGERATED_VERB>"]
            elif suffix == -1:
                suffix = translation_dictionary["<GENTLE_VERB>"]

            if trailing_punctuation.endswith("?"):
                suffix += " lunk"
            elif trailing_punctuation.endswith("."):
                suffix += "$"
        except KeyError:
            pass

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

        if is_plural and from_actor_form(word) != word and (to_actor_form(word).find("erser") != -1):
            #return "a"
            is_actor = True
        if is_actor_form(word):
            #return "b"
            is_actor = True

        if is_actor:
            if singular:
                singular = from_actor_form(singular)
            else:
                plural = inflect_engine.plural(from_actor_form(plural))

            word_suffix += translation_dictionary["<ACTOR>"]
        
        if is_actor and singular == plural:
            is_plural = True
            singular = to_actor_form(singular)
            plural = inflect_engine.plural(singular)

        if plural in ignored_plurals:
            is_plural = False

        #return f"{is_plural, from_actor_form(word), word, to_actor_form(word)}"
        #return from_actor_form(word)
        #return f'{"singular:", singular, "plural:", plural, "is plural:", is_plural, "is actor:", is_actor}'

        try:
            found = False

            # key = Gorgus, value = English
            for key, value in translation_dictionary.items():
                if type(value) == str:
                    
                    if value == singular or plural == inflect_engine.plural(value):
                        found = True
                        if not is_plural:
                            translated += f"{key}{word_suffix}{suffix} "
                        else:
                            translated += f"{translation_dictionary['<PLURAL>']}{key}{word_suffix}{suffix} "
                        break
                elif type(value) == list:
                    for possible_word in value:
                        if possible_word == singular or plural == inflect_engine.plural(possible_word):
                            found = True
                            if not is_plural:
                                translated += f"{key}{word_suffix}{suffix} "
                            else:
                                translated += f"{translation_dictionary['<PLURAL>']}{key}{word_suffix}{suffix} "
                            break
                if found: break

            if not found:
                translated += f"{word} "
        except KeyError:
            translated += f"{word} "
    translated = replace_word(translated, "really", translation_dictionary["<EXAGGERATED_VERB>"])
    translated = replace_word(translated, "extremely", translation_dictionary["<EXAGGERATED_VERB>"])
    translated = replace_word(translated, "kinda", translation_dictionary["<GENTLE_VERB>"])

    return translated

def from_gorgus(user_input: str):
    translated = ""

    # Replace phrases with english words      
    for gorgus, english in phrase_translations.items():
        if type(english) == list:
            for phrase in english:
                user_input = user_input.replace(gorgus, english[0])
        elif type(english) == str:
            user_input = user_input.replace(gorgus, english)

    words = user_input.split(" ")

    for word in words:
        if word == "lunk":
            translated = translated[:-1] + "?"
            continue

        suffix = ""
        trailing = get_trailing_punctuation(word)

        if trailing.endswith("$"):
            suffix += "."

        word = word.translate(str.maketrans('', '', ".,?!$"))

        plural = False
        actor = False
        if word.startswith(translation_dictionary["<PLURAL>"]):
            word = word.removeprefix(translation_dictionary["<PLURAL>"])
            plural = True

        if word.endswith(translation_dictionary["<ACTOR>"]):
            word = word.removesuffix(translation_dictionary["<ACTOR>"])
            actor = True

        if word.endswith(translation_dictionary["<EXAGGERATED_VERB>"]):
            word = word.rstrip(translation_dictionary["<EXAGGERATED_VERB>"])
            translated += "really "
        if word.endswith(translation_dictionary["<GENTLE_VERB>"]):
            word = word.rstrip(translation_dictionary["<GENTLE_VERB>"])
            translated += "kinda "

        if word == "ji":
            translated += "ji "
            continue

        try:
            translation = translation_dictionary[word]

            if type(translation) == str:
                if actor:
                    translation = to_actor_form(translation)

                if plural:
                    translation = inflect_engine.plural(translation)

                translated += f"{translation}{suffix} "
            elif type(translation) == list:
                final = translation[0]

                if actor:
                    final = to_actor_form(final)

                if plural:
                    final = inflect_engine.plural(final)

                translated += f"{final}{suffix} "
        except KeyError:
            translated += f"{word}{suffix} "
    translated = swap_verbs_and_adverbs(translated)
    translated = fix_articles(translated, "ji")

    return translated

def fix_up(translated: str, user_input: str, user_choice: int):
    translated = translated.capitalize().strip()
    return translated

    '''if translated.endswith("?") and user_choice == 2:
        translated = translated[:-2] + "?"'''

    """if not translated.endswith(".") and not translated.endswith("!") and not translated.endswith("?") and not translated.endswith("lunk"):
        punctuation = ""
        questions = ["who", "what", "when", "where", "how", "were", "why"]
        words = [word.lower() for word in translated.split(" ")]

        if user_choice == 1:
            if user_input.endswith("."):
                punctuation = translation_dictionary["<SENTENCE_END>"]
            elif user_input.endswith("?"):
                punctuation = " lunk"
        elif user_choice == 2:
            if user_input.endswith(translation_dictionary["<SENTENCE_END>"]):
                punctuation = "."
        translated += punctuation

        if punctuation == "":

            if not translated.endswith("?") and not translated.endswith(".") and not translated.endswith(translation_dictionary["<SENTENCE_END>"]):# and user_choice == 1:

                for gorgus,eng in translation_dictionary.items():
                    if type(eng) == list:
                        if gorgus in words and eng[0] in questions:
                            punctuation = " lunk"
                            break

                        if eng[0] in questions and eng[0] in words:
                            punctuation = "?"
                            break
                    elif type(eng) == str:
                        if gorgus in words and eng in questions:
                            punctuation = " lunk"
                            break

                        if eng in questions and eng in words:
                            punctuation = "?"
                            break
            else:
                if user_choice == 1:
                    if user_input.endswith("?"):
                        punctuation = " lunk"

            if user_choice == 1: # translate from english
                translated = translated + punctuation
            elif user_choice == 2: # translate to english
                if punctuation == "lunk":
                    translated = translated[:-3] + ""
                elif punctuation == ".":
                    translated = translated + punctuation
                else:
                    translated = translated + punctuation"""


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
            # Modify 'quickly' by adding '\u0302' and remove 'very'
            words[i + offset] = words[i + offset] + replacement
            del words[i]  # Remove 'very'

            # Break after the first occurrence is handled
            break

    # Join the words back into a string and return
    return " ".join(words)

def translate(text: str, to: Literal["english", "gorgus"]):
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

    translated = fix_up(translated, text, user_choice)

    return translated