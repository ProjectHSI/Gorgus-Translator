@echo off
echo Installing...

pip install -U pip setuptools wheel
pip install -U 'spacy[cuda11x]'
pip install -r requirements.txt
python -m spacy download en_core_web_sm

echo Done!
pause