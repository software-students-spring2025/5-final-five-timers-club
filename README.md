# Emotify: Emotion Detection and Music Recommendation

[![Lint-free](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/lint.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/lint.yml)

[![ML Client CI](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/ml-client-ci.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/ml-client-ci.yml)

[![Web App CI](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/webapp-ci.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-five-timers-club/actions/workflows/webapp-ci.yml)

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

## 🗂️ Project Structure

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

## 🔐 Environment Configuration

Create a `.env` file in your project root folder with the following variables:

## Running the Project

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
