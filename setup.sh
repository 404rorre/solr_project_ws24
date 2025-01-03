#!/bin/bash
# setup.sh

# Function to check if a command exists
check_command() {
    if ! command -v $1 &>/dev/null; then
        echo "Error: $1 is required but not installed."
        exit 1
    fi
}

# Check Python version
check_python_version() {
    if ! command -v python3.12 &>/dev/null; then
        echo "Error: Python 3.12.7 is required but not found."
        echo "Please install Python 3.12.7 before running this script."
        exit 1
    fi

    version=$(python3.12 -V 2>&1 | awk '{print $2}')
    if [[ "$version" != "3.12.7" ]]; then
        echo "Error: Python 3.12.7 is required, but found version $version"
        exit 1
    fi
}

# Check for required commands
check_command curl
check_command tar

# echo "Setting up Python environment..."
# check_python_version

echo "Creating virtual environment..."
python3.12 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing Python requirements..."
pip install -r requirements.txt

echo "Python environment setup complete!"

echo "Setting up data directories..."
# Create base directory if it doesn't exist
mkdir -p data/{index,qrel,topics}

# Change to data directory
cd data || exit 1

# Download files with progress bars
echo "Downloading cord-19_2020-07-16.tar.gz..."
curl -L -O https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_2020-07-16.tar.gz

echo "Downloading topics-rnd5.xml..."
curl -L https://ir.nist.gov/trec-covid/data/topics-rnd5.xml -o topics/topics-rnd5.xml

echo "Downloading qrels-covid_d5_j0.5-5.txt..."
curl -L https://ir.nist.gov/trec-covid/data/qrels-covid_d5_j0.5-5.txt -o qrel/qrels-covid_d5_j0.5-5.txt

# Extract the main archive
echo "Extracting cord-19_2020-07-16.tar.gz..."
tar xf cord-19_2020-07-16.tar.gz

# Move metadata.csv to index directory
echo "Moving metadata.csv to index directory..."
mv 2020-07-16/metadata.csv index/

echo "Setup complete!"

