
# Document-based GPT Application for Question Answering

This is a Question-Answering application with separate backend and frontend services, utilizing Docker for containerization and Makefile for easy management.

## Project Structure

The project consists of the following main components:

- Backend service
- Frontend service
- Makefile for building and running the application
- Docker Compose for orchestrating the services

## Prerequisites

- Docker
- Docker Compose
- Make

## Environment Variables

The application uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

---
```
BACKEND_PORT=8000
FRONTEND_PORT=8501
OLLAMA_PORT=11434
OLLAMA_BASE_URL=http://ollama:11434
UPLOADS_DIR=./uploads
```
---

For production, create a `.env.production` file with appropriate values.

### Installation

1. Clone the repository:

---

```
   git clone git@github.com:Avyukth/open-llm-rag.git
   cd open-llm-rag
```

---

2. Build and run the system using the provided Makefile:

---

```
   make up SERVICE1=backend SERVICE2=frontend
```



## Building the Application

To build both backend and frontend Docker images:

---
```
make build
```
---

To build individual services:

---
```
make backend
make frontend
```
---

## Running the Application

To run both services:

---
```
make up SERVICE1=backend SERVICE2=frontend
```
---

## Stopping the Application

To stop all services:

---
```
make stop
```
---

## Viewing Logs

To view logs from all services:

---
```
make logs
```
---

## Development Helpers

To open a shell in the backend container:

---
```
make shell-backend
```
---

To open a shell in the frontend container:

---
```
make shell-frontend
```
---

## Cleaning Up

To clean up Docker system (use with caution):

---
```
make clean
```
---

## Available Make Commands

For a full list of available commands:

---
```
make help
```
---

## AI Model Support

**Note: Important Information About AI Model Support**

Currently, this application is configured to work with Ollama for its AI model needs. However, the architecture has been designed with the capability to support other AI providers such as OpenAI and Cohere.

- **Ollama**: Fully implemented and tested.
- **OpenAI**: The codebase includes support for OpenAI, but it has not been thoroughly tested due to budget constraints.
- **Cohere**: Similar to OpenAI, support for Cohere is included in the codebase but has not been extensively tested.


## Docker Images

- Backend Image: `localhost/qa-app-backend:0.1.0`
- Frontend Image: `localhost/qa-app-frontend:0.1.0`

## Additional Notes

- The application uses Python 3.10
- Docker Compose file is located at `deployments/docker-compose.yml`
- Dockerfiles are located in the `deployments/docker/` directory

## Troubleshooting

If you encounter any issues, please check the logs using `make logs` and ensure all required environment variables are set correctly.

For more detailed information about each service, refer to their respective documentation in the `backend/` and `frontend/` directories.
