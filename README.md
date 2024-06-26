# Description

This project is designed to revolutionize the way you consume news by offering concise summaries of original news articles. The primary goal is to help you save time by providing short versions of articles that capture the main points and essential information. Instead of reading lengthy articles, you can quickly grasp the core message and stay informed efficiently. Whether you're on the go or just looking to streamline your news intake, our service ensures you get the information you need without the extra reading time.

**NewsHub:** Your shortcut to staying informed. Dive into concise summaries of top stories and save time without compromising on knowledge.

![Facebook cover - 1 (3)](https://github.com/casual-user-asm/NewsHub/assets/82218252/5c7431a2-b203-4070-a11c-b05baf6585d4)
*New news sources will be added to the website on a weekly basis.

# Project Setup

The app contains 2 views:

- Home view - Here are the news sources where you can view information about them and choose which source you want to read news from.
- Detail view - Here you can read the main news from the selected news source. You will see the headline and a short version of the news text, which has been condensed and summarized by the Llama3 neural network. If the short version of the text is not sufficient for you, you can proceed to read the original news article via the link provided on the page.

---

You can also clone the project and run it with Docker(the Docker instruction below) or enjoy the preview video below instead :smile:


https://github.com/casual-user-asm/NewsHub/assets/82218252/f3ef94a9-66b9-420a-8ac4-67c38f097c7c


## Running the Project with Docker

### Prerequisites
- **Docker**: Ensure Docker is installed on your machine. You can download it from [Docker's official website](https://www.docker.com/get-started).
- **Docker Compose**: Make sure it's installed as well. You can find installation instructions [here](https://docs.docker.com/compose/install/).

### Getting Started

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/casual-user-asm/NewsHub.git
    cd yourproject
    ```

2. **Create and Configure `.env` File**:
    - Create the `.env` file to add any necessary configuration values (e.g., database URLs, API keys).
    - Below are the common configuration fields you may need to set in your .env file.
      # Debug mode (set to True for development)
        DEBUG=True
        
      # Django secret key
        SECRET_KEY=*
      
      - Run this command in your terminal to generate a new secret key:
         ```bash
         python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
         ```
        
      # PostgreSQL database settings
        - DATABASE_NAME=postgres
        - DATABASE_USER=postgres
        - DATABASE_PASSWORD=postgres
        - DATABASE_HOST=my_postgres
        - DATABASE_PORT=5432
        
      # API key for Groq
       GROQ_API_KEY=*
       
     For the `GROQ_API_KEY`, you'll need to obtain it from the Groq website. Follow these steps:
     - Go to [Groq's website](https://groq.com/).
     - Click on 'GroqCloud'.
     - In GroqCloud, you can create your API key.

3. **Build the Docker Images**:
    - Using `docker-compose.yml`:
        ```sh
        docker-compose build
        ```

4. **Run the Containers**:
    - Using Docker Compose:
        ```sh
        docker-compose up -d
        ```
