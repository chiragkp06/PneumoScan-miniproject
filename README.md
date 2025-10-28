Cloud-Based Pneumonia Detection

Overview
This is a cloud-based web application designed to assist radiologists in detecting pneumonia from chest X-ray images using machine learning and AWS cloud services. It automates the process of uploading, analyzing, and storing medical images and results.

Project Objective
Enable radiologists to upload chest X-ray images and get automated pneumonia detection with a confidence score.

Display results clearly on a secure dashboard and allow downloading of medical reports.

Store all image data and results securely using AWS RDS and S3.

Tech Stack
- Frontend
- HTML5
- CSS3
- JavaScript


Backend
- Python 3
- Flask (REST API)
- MySQL (AWS RDS)

AWS Services
- Amazon Rekognition – to detect pneumonia from X-ray images
- Amazon S3 – to store uploaded images securely
- Amazon RDS (MySQL) – to store user data and detection results

Other Tools
boto3 (AWS SDK for Python)

dotenv – for managing API keys and secrets using a .env file
