@echo off
REM setup.bat

echo Checking Python version...
python --version 2>nul | find "3.12.7" >nul
if errorlevel 1 (
    echo Error: Python 3.12.7 is required but not found.
    echo Please install Python 3.12.7 before running this script.
    exit /b 1
)

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing Python requirements...
pip install -r requirements.txt

echo Python environment setup complete!

echo Setting up data directories...
mkdir data\index 2>nul
mkdir data\qrel 2>nul
mkdir data\topics 2>nul

cd data

echo Downloading files...
echo Downloading cord-19_2020-07-16.tar.gz...
curl -L -O https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_2020-07-16.tar.gz
if errorlevel 1 (
    echo Error downloading cord-19_2020-07-16.tar.gz
    exit /b 1
)

echo Downloading topics-rnd5.xml...
curl -L https://ir.nist.gov/trec-covid/data/topics-rnd5.xml -o topics\topics-rnd5.xml
if errorlevel 1 (
    echo Error downloading topics-rnd5.xml
    exit /b 1
)

echo Downloading qrels-covid_d5_j0.5-5.txt...
curl -L https://ir.nist.gov/trec-covid/data/qrels-covid_d5_j0.5-5.txt -o qrel\qrels-covid_d5_j0.5-5.txt
if errorlevel 1 (
    echo Error downloading qrels-covid_d5_j0.5-5.txt
    exit /b 1
)

echo Extracting cord-19_2020-07-16.tar.gz...
tar xf cord-19_2020-07-16.tar.gz
if errorlevel 1 (
    echo Error extracting archive
    exit /b 1
)

echo Moving metadata.csv to index directory...
move 2020-07-16\metadata.csv index\
if errorlevel 1 (
    echo Error moving metadata.csv
    exit /b 1
)

echo Setup complete!
cd ..