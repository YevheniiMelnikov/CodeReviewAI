# Code Review AI

This project is a tool that integrates GitHub, OpenAI, and Redis to perform automated code reviews using GPT models.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/YevheniiMelnikov/CodeReviewAI

2. **Create .env file**

    In the root of the project, create a .env file and add the following environment variables:

 - GITHUB_TOKEN
 - OPENAI_API_KEY
 - REDIS_URL

3. **Run the project with DOCKER**
   ```bash
   docker-compose up --build
   ```

4. **Make POST request to http://127.0.0.1:8000/review**

## Scaling the System

To handle over 100 review requests per minute and large repositories with many files, the system can use microservices. A message queue (like RabbitMQ or Kafka) would distribute tasks, while worker nodes process GitHub and OpenAI requests in parallel. Redis caching helps avoid repeated API calls. To handle API rate limits and costs, techniques like rate limiting, retries, and cost monitoring would be employed.
