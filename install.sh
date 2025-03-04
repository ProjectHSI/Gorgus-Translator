#!/bin/bash
echo "Installing..."

pip3 install -r requirements.txt && echo "Installed packages successfully!" || echo "Failed to install packages!"
python3 -m spacy download en_core_web_sm && echo "Installed needed Spacy AI models!\n\nDone!" || echo "Failed to install needed Spacy AI models!"
