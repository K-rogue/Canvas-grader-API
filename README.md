# Canvas Feedback Uploader

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)

## Description

Canvas Feedback Uploader is a Python script that simplifies the process of uploading feedback files to Canvas assignments. It leverages the Canvas API to notify Canvas about the file, upload the file, and then updates the assignment submission with the attached feedback.

## Features

- **Easy Integration:** Quickly integrate feedback files into Canvas assignments.
- **Dynamic File Handling:** Automatically detects file name, size, and content type.
- **Error Handling:** Detailed error messages and debugging information for troubleshooting.

## Prerequisites

- Python 3.8 or higher
- Install required Python packages using `pip install -r requirements.txt`

## Usage

1. Configure your Canvas API credentials in the script (`api_url`, `access_token`).
2. Run the script: `python upload_feedback.py`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/K-rogue/canvas-feedback-uploader.git
