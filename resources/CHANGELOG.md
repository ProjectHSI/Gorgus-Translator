# Changelog
The Gorgus Translator was published to Github in version `1.6`, pretty much all prior versions are lost media lmao.

## Version 1.11 (current)
- IT WASN'T THE LAST UPDATE! I have found motivation to KEEP working on this!
- With the help of @projecthsi on Discord, we're turning the Gorgus Translator into a website!
- We're migrating from using spaCy to NLTK, which will help with dependency issues, will help with the migration to a web translator, etc...
- Added a little warning on start that translations are a little broken while we migrate.
- Added more words.

## Version 1.10 
- I'm going to add content to this over time, but this will be the last update cause I'm getting bored of working on this translator lol.
- Added **A LOT** of new words! `(500+! :D)`
- Fixed some bugs.
- You can now turn any verb into past tense by adding `-ra` *(eat -> ate, build -> built)* or continuous tense by adding `-ak` *(eat -> eating, kill -> killing)*.
- Improved grammar when translating from Gorgus to English and vice versa.
- Added more loading screen messages.
- Removed Herobrine.

## Version 1.95
- You can now host a multiplayer game between you and a friend! Check out the new game. :)
- A server list will detect servers running on the same WiFi.

## Version 1.9
- Added a `Games` tab to the translator! You can only play Gorgus Worlde and Hangman for now though lol.
- Added more words and phrases.
- Added some info to the loading screen so you don't have to stare at nothing for a while.

## Version 1.8
- Small optimization update.
- Couple more words and phrases. (300+ words reached!!! :D)
- Added some tooltips to the settings menu.
- Fixed some bugs.
- The full stop in the language is now set back to a regular full stop.
- Some words have accents on them now to help with pronounciation! (can be turned off in settings)
- Changed how the settings tab looks.
- You can clear your settings in the settings menu now!

## Version 1.75
- Added some language features.
- Punctuation like "," and "!" is now supported in the translator!
- Added quite a few more words.

## Version 1.7
- Small update, just some new words. (We now have 200+ words! :D)
- You can now turn words into `"a person who X"`, basically meaning `"kill"` becomes `"killer"` or `"a person who kills"`. You do this by adding the suffix "-ak" to a noun.
- Fixed translation bugs.
- Added `gitpython` and `nltk` to `requirements.txt` so it would be automatically installed.
- Modules inside of the `requirements.txt` file are automatically installed when openning the program for the first time.
- Allowed the user to disable or enable the clock in the top right.
- Users can check for updates in the settings menu without restarting now.
- Moved a lot of the informal words to the bottom of the dictionary lol.
- Changed the translator page a lil' bit.

## Version 1.65
- Added a `Settings` page to the UI which will be expanded in the future
- Automatic update checker! Turn it off in the `Settings` page.
- Improved the dictionary search a tiny bit.
- Your theme settings now save and can be found in the `Settings` page.
- Removed redundant dependency.

## Version 1.6
- **UI update!!!!!** I'm using the `textual` library instead of the regular python console now, so we have a UI!!!
- Added `Dictionary` page to the UI
- Added `Credits` page to the UI
- The translate to and from English and Gorgus pages are now in one `Translator` page

## Version 1.5
- Added accents on verbs and nouns to make them more aggressive/exaggerated
- Added some language stats to the menu like the number of words in the language
- Improved loading times when going from the selected section to the menu
- Removed a message from the title screen
- Articles are now automatically handled by the translator
- Added more words
- Started using language tagging for more accurate translation to English
- There are some known issues with verbs and adjectives getting tagged when converting back to English

## Version 1.4
- Started using the `inflect` Python library! While this may increase load times, this will allow for many new language features!
- Fixed typo in the changelog.
- Fixed a bug where the screen didn't clear correctly.

## Version 1.3
- Added the changelog to the menu!
- Added some more English words to the translation.
- Made some small grammar modifications, plans are that 1.4 will improve grammar when translating to English.

## Version 1.2
- Added *basic* grammar support.
- Implemented full stops in the translations in the form of "$". This means that a full stop in English translates to the full stop in Gorgus.

## Version 1.1
- Can't remember what I added this update.

## Version 1.0
- Initial program
