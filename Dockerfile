Dockerfile
Use a Python 3.13-slim image for a small container size
FROM python:3.13-slim

Set the working directory inside the container
WORKDIR /app

Install system dependencies
RUN apt-get update && apt-get install -y mariadb-client-10.11

Copy the dependencies file and install Python packages
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

Copy the rest of the application code
COPY . /app

Expose port 8000
EXPOSE 8000

Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]