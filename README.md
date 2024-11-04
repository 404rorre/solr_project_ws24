# solr_project_ws24
Building and optimizing an information retrieval system for COVID-19 research papers using Apache Solr. 

*Project for DIS17.1 - Search Engine Technology, TH Köln, WS 2024*

# Setup Guide for TREC-COVID Project

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Python 3.12.7**
   - Download from [Python's official website](https://www.python.org/downloads/)
   - Verify installation by running: `python --version`

2. **Git**
   - Download from [Git's official website](https://git-scm.com/downloads)
   - Verify installation by running: `git --version`

3. **Disk Space**
   - At least 10GB of free disk space
   - The CORD-19 dataset is approximately 3.7GB compressed

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd solr_project_ws24
   ```

2. **Run the Setup Script**

   For Windows:
   ```bash
   setup.bat
   ```

   For Linux/MacOS:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   The setup script will:
   - Create a Python virtual environment
   - Install all required packages
   - Download and organize the TREC-COVID dataset
   - This process may take several minutes depending on your internet connection

## Verifying the Installation

After the setup is complete, verify that:

1. The `.venv` directory exists
2. The `data` directory contains the following structure:
   ```
   data/
   ├── 2020-07-16/
   ├── index/
   ├── qrel/
   └── topics/
   ```

## Working with the Virtual Environment

- The virtual environment will be activated automatically during setup
- To manually activate/deactivate:

  Windows:
  ```bash
  # Activate
  .venv\Scripts\activate.bat
  # Deactivate
  deactivate
  ```

  Linux/MacOS:
  ```bash
  # Activate
  source .venv/bin/activate
  # Deactivate
  deactivate
  ```

## Troubleshooting

Common issues and solutions:

1. **Python version error**
   - Ensure Python 3.12.7 is installed and in your system PATH
   - Try running `python --version` to verify

2. **Download failures**
   - Check your internet connection
   - Try running the setup script again
   - Verify you have enough disk space

3. **Permission errors**
   - Windows: Run as Administrator
   - Linux/MacOS: Use `sudo` if necessary for installations

## Getting Help

If you encounter any issues not covered in this guide:
1. Check the project's issue tracker on GitHub
2. Create a new issue with:
   - Your operating system and version
   - Error messages (if any)
   - Steps to reproduce the problem

## Next Steps

Once setup is complete, you can start using the project. Refer to the project documentation for usage instructions and examples.
