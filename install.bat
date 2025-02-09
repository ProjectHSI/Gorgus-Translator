@echo off
echo Installing...

pip install -r requirements.txt
python -m spacy download en_core_web_sm

echo Done!
pause