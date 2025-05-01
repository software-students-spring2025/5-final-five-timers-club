![Lint-free](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/lint.yml/badge.svg?branch=)
![Machine Learning Client CI](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/ml-client-ci.yml/badge.svg?branch=)
![Web App CI](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/webapp-ci.yml/badge.svg?branch=)

# Emotify: Emotion Detection and Music Recommendation

## Description

This project is an application that detects a user's emotions from their facial expressions and recommends music based on their expression. The system processes webcam images to identify emotions and uses Spotify's API to play songs that match the detected emotion.

## Team Members

[Oluwapelumi Adesiyan](https://github.com/oadesiyan) <br />
[Polina Belova](https://github.com/polinapianina) <br />
[Gabriella Codrington](https://github.com/gabriella-codrington) <br />
[Maya Mabry](https://github.com/mam10023) <br />

## Overview of System Architecture

This system consists of three interconnected components:

- **Machine Learning Client** - Captures webcam images, detects facial emotions using DeepFace, and requests matching songs from Spotify's API.
- **Web Application** - A Flask-based frontend that lets users capture images, trigger emotion detection, and view their emotion history with recommended songs.
- **MongoDB Database** - Stores emotion detection history and song recommendations for user tracking and review.

## Prerequisites

Ensure the following tools are installed:

- Python 3.11+
- MongoDB
- Spotify Developer Account (for API access)
- Docker and Docker Compose

## 🗂️ Project Structure

```
.
├── web-app/ # Flask frontend
│ ├── app.py # Main web app logic
│ ├── auth.py # User authentication
│ ├── requirements.txt # Requirements
│ ├── templates/ # HTML templates
│ └── static/ # CSS and JavaScript
├── machine-learning/ # Emotion detection service
│ ├── face_recog.py # Facial emotion detection
│ ├── get_playlist.py # Spotify API integration
│ └── requirements.txt # Requirements
└── README.md # You are here
```

## 🔐 Environment Configuration

Create a `.env` file in your project root folder with the following variables:

## Running the Project

The README has already been created as a Markdown file that you can copy and paste with all the formatting intact. Here is the complete Markdown content:
markdown# Emotion Playlist

The Emotion Playlist project consists of two main microservices:

1. **Web Application Service (Flask)**: A Python-based web application built with Flask that handles user authentication, emotion history, and provides the web interface for users to interact with the application.

2. **Machine Learning Service**: A specialized service that handles face detection, emotion recognition using DeepFace, and Spotify API integration to recommend songs based on detected emotions.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Git
- Spotify Developer account (for API credentials)
- MongoDB account (for database storage)

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/software-students-spring2025/5-final-five-timers-club
   cd 5-final-five-timers-club
   ```

2. Create environment variables file:

   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your specific configuration if needed.

4. Start the application with Docker Compose:

   ```bash
   docker-compose up -d
   ```

5. The application will be running at http://127.0.0.1:6001

## Deployed Site

Access the site, deployed through DigitalOcean [here](http://165.22.180.89:5001/login)!

## Environment Configuration

The application requires the following environment variables, which can be set in the `.env` file:

- `CLIENT_ID`: Your Spotify API client ID
- `CLIENT_SECRET`: Your Spotify API client secret
- `MONGO_URI`: MongoDB connection URI (default: mongodb://localhost:27017/emotion_playlist)
- `SECRET_KEY`: Secret key for Flask session encryption

## Database Configuration

The application uses MongoDB to store:

- User account information
- Detected emotions history
- Recommended songs for each emotion

The database is automatically initialized when the application starts.

## Application Structure

The project is organized into two main services, each with its own Dockerfile:

### 1. Machine Learning Service (./machine-learning)

- Face recognition and emotion detection using DeepFace
- Spotify API integration for song recommendations
- REST API endpoints for emotion detection and song retrieval
- Accessible at http://127.0.0.1:6001

### 2. Web Application Service (./web-app)

- User authentication and session management
- Webcam capture and processing
- Emotion and song history display
- User interface for interacting with the system
- Accessible at http://127.0.0.1:5001

## API Documentation

The machine learning service provides the following API endpoints:

**Emotion Detection**

- `POST /detect`: Analyze a base64-encoded image and return the detected emotion

**Spotify Integration**

- `GET /token`: Retrieve a Spotify API token
- `POST /playlist`: Get a song recommendation based on detected emotion

The web app provides the following routes:

**User Interface**

- `GET /`: Home page with webcam capture
- `GET /my-songs`: View history of emotions and recommended songs

**Authentication**

- `GET /login`: Login page
- `POST /login`: Process login
- `GET /register`: Registration page
- `POST /register`: Process registration
- `GET /logout`: Logout

**API Endpoints**

- `POST /submit-video`: Process webcam capture for emotion detection

## Development Setup

### Local Development with Docker

1. Clone the repository:

   ```
   git clone https://github.com/software-students-spring2025/5-final-five-timers-club.git
   cd 5-final-five-timers-club
   ```

2. Create environment variables file:
   cp .env.example .env

3. Edit the `.env` file with your development configuration.

4. Build and start the containers using Docker Compose:
   docker-compose up -d --build

5. The application will be running at http://127.0.0.1:6001

6. To stop the containers:
   docker-compose down

## Features

- **User Authentication** - Register and login to track your history
- **Facial Emotion Detection** - Detects emotions from webcam images (happy, sad, angry, fearful, surprised, disgusted, neutral)
- **Music Recommendations** - Suggests songs from Spotify based on your detected emotion
- **History** - Review your past detected emotions and recommended songs

## Technologies Used

- **Flask** - Python web framework
- **DeepFace** - Deep learning facial recognition and emotion detection
- **Spotify Web API** - Music recommendation engine
- **MongoDB** - Database for emotion and song history
- **Flask-Login** - User authentication system
- **OpenCV** - Image processing
