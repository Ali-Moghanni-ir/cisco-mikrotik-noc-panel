# Use a lightweight, official Python runtime as a parent image
FROM python:3.11-slim

# Install system-level dependencies required by Netmiko and Ansible (SSH)
RUN apt-get update && apt-get install -y \
    openssh-client \
    sshpass \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /opt/montazeri-noc

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 5000 for the web interface
EXPOSE 5000

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Boot the application using Gunicorn (Production Server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]