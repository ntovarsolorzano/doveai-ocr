# DoveAI OCR

DoveAI OCR is a web application that uses MistralAI's OCR capabilities to extract text from PDF files and images, and convert it to Markdown format. The application also allows users to paste text directly and convert it to Markdown.

## Features

- Upload PDF files and images for text extraction
- Paste text directly for conversion to Markdown
- View extracted text in Markdown format
- Preview rendered Markdown
- Copy extracted text to clipboard
- Download extracted text as a Markdown file
- Dark mode support
- Responsive design
- Docker support for easy deployment

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **OCR Engine**: MistralAI OCR
- **Deployment**: Docker, Docker Compose

## Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- MistralAI API key (sign up at [MistralAI](https://mistral.ai/))

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/doveai-ocr.git
   cd doveai-ocr
   ```

2. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your MistralAI API key:
   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   ```

4. Build and start the Docker containers:
   ```bash
   docker-compose up -d
   ```

5. Access the application at [http://localhost](http://localhost)

## Development Setup

If you want to run the application without Docker for development:

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set the environment variable for the MistralAI API key:
   ```bash
   # On Linux/Mac
   export MISTRAL_API_KEY=your_mistral_api_key_here
   
   # On Windows
   set MISTRAL_API_KEY=your_mistral_api_key_here
   ```

5. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend

The frontend is static HTML, CSS, and JavaScript, so you can simply open the `frontend/index.html` file in your browser. However, for API calls to work, you'll need to ensure the backend server is running.

## API Endpoints

- `POST /api/upload`: Upload a file for OCR processing
- `POST /api/extract`: Extract text from a file or direct text input
- `POST /api/convert`: Convert text to markdown format

## License

[MIT License](LICENSE)

## Acknowledgements

- [MistralAI](https://mistral.ai/) for providing the OCR capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Marked.js](https://marked.js.org/) for Markdown rendering
