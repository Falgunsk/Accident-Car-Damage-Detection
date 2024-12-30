# Accident-Car-Damage-Detection
# 🤖 AI-Based Accident Damage Detection and Repair Cost Estimation

An AI-powered Vehicle Damage Detection System designed to detect and estimate repair costs for damaged car parts based on uploaded images. This system utilizes YOLOv8 for object detection and provides a user-friendly web interface built with Flask. It aims to streamline the process of vehicle damage assessment, making it efficient for insurance companies and repair centers to evaluate repair costs.

## 🔍 Table of Contents
- [🚗 Project Overview](#project-overview)
- [⚙️ Features](#features)
- [🛠️ Technologies Used](#technologies-used)
- [🔧 Setup and Installation](#setup-and-installation)
- [💻 Usage](#usage)
- [🤖 Model Information](#model-information)
- [🚀 Future Improvements](#future-improvements)

## 🚗 Project Overview

The Vehicle Damage Detection System allows users to upload images of cars to detect damaged parts and estimate repair costs. It includes functionalities such as:

- Damage detection for parts like:
  - 🚗 Bonnet
  - 🚗 Bumper
  - 🚗 Dickey
  - 🚗 Door
  - 🚗 Fender
  - 🚗 Light
  - 🚗 Windshield
- Highlighting detected damaged parts in the image.
- Estimating repair costs based on the detected damage.
- Integrating with a MySQL database to manage user details, car information, spare parts, and repair costs.

### Key Objectives:
- **🔍 Damage Detection**: Accurately detect damaged car parts using state-of-the-art object detection models.
- **💸 Cost Estimation**: Provide reliable repair cost estimates based on the damage.
- **📃 Database Integration**: Ensure seamless data management through MySQL.
- **🔹 User-Friendly Interface**: Offer an intuitive web-based experience for users.

## ⚙️ Features

- **🔍 Object Detection**: Use YOLOv8 to detect and highlight damaged car parts.
- **💸 Cost Estimation**: Estimate repair costs for detected damages.
- **🔍 Image Upload**: Enable users to upload car images easily.
- **⏳ Real-Time Results**: Display detection results and estimated costs instantly.
- **📃 Database Management**: Store relevant data including user information, car details, and repair costs.
- **🎨 Visual Damage Display**: Provide an option to view and download images with damage highlighted.

## 🛠️ Technologies Used

### Backend:
- Python
- YOLOv8 (Object Detection)
- MySQL (Database Management)

### Frontend:
- HTML
- CSS
- 
### Libraries:
- Flask ( Web Framework)
- Pandas (Data Analysis)
- Pillow (Image Processing)
- ultralytics (YOLOv8 Integration)
- regex (Regular Expressions)
- mysql-connector-python (MySQL Interaction)

## 🔧 Setup and Installation

### Prerequisites
- 🔹 Python 3.9.13
- 🔹 MySQL Server
- 🔹 Virtual Environment (Optional but Recommended)

### Installation Steps

1. **🔍 Clone the Repository:**

    ```bash
    git clone https://github.com/Falgunsk/Accident-Car-Damage-Detection.git
    cd Accident-Car-Damage-Detection
    ```

2. **🔧 Install Required Packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **📃 Set Up MySQL Database:**

    - Create a new MySQL database.
    - Update database credentials in the `config.py` file:

      ```python
      DB_HOST = 'localhost'
      DB_USER = 'root'
      DB_PASSWORD = 'yourpassword'
      DB_NAME = 'vehicle_damage_detection'
      ```

4. **🚀 Run the Application:**

    ```bash
    python app.py
    ```

## 💻 Usage

1. **🔓 Sign Up**: Register by entering personal details and vehicle information.
2. **🔐 Log In**: Access the system using your credentials.
3. **🔍 Upload Image**: Submit an image of the damaged vehicle for analysis.
4. **⏳ View Results**: See the detected damages and their estimated repair costs.
5. **🗄 Download Image**: Save the image with highlighted damages if needed.

## 🤖 Model Information

- **🔍 YOLOv8 Object Detection**:
  - Trained on a custom dataset comprising vehicle parts such as the bonnet, bumper, dickey, door, fender, light, and windshield.
  - Offers high accuracy in detecting and assessing damage.

## 🚀 Future Improvements

- **🌐 Multi-language Support**: Expand support for multiple languages.
- **🛠️ Damage Severity Analysis**: Enhance the system to evaluate the severity of damage.
- **📚 Insurance Integration**: Provide integration with insurance platforms for smoother claim processing.
- **📱 Mobile App**: Develop a mobile application for on-the-go usage.

