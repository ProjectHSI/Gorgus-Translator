def is_verb(word):
    # A basic check for verbs (you can expand this list or use a regex)
    common_verbs = ["run", "runs", "ran", "jump", "jumps", "jumped", "walk", "walks", "walked", "is", "are", "was", "were", "ate", "eat", "eats", "approach", "approaches", "approached"]
    return word.lower() in common_verbs

def is_adverb(word: str):
    # A basic check for adverbs (commonly end in 'ly')
    other_adverbs = [
        "fast",
        "often",
        "too"
    ]

    return word.lower().endswith("ly") or word.lower() in other_adverbs

def swap_verbs_and_adverbs(sentence: str):
    # Split sentence into words
    words = sentence.split(" ")
    
    # Iterate through words and swap verbs with following adverbs
    i = 0
    while i < len(words) - 1:
        if is_verb(words[i]) and is_adverb(words[i+1]):
            # Swap the verb and adverb
            words[i], words[i + 1] = words[i + 1], words[i]
            i += 2  # Move past the swapped pair
        else:
            i += 1

    # Reconstruct the sentence
    return " ".join(words)