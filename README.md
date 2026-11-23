# smart-agriculture-crop-management
A web-based Smart Agriculture and Crop Management System built with Python, MySQL, HTML, CSS, and JavaScript. It helps farmers manage farms, fields, crops, planting cycles, farming activities, expenses, and reports, while providing administrators with centralized farmer and agricultural data management.






# 🌱 Smart Agriculture & Crop Management System

A web-based agricultural management platform designed to help farmers manage their agricultural activities digitally and enable administrators to monitor and manage farmer-related information through a centralized dashboard.

## 📌 Project Overview

The **Smart Agriculture & Crop Management System** is designed to make agricultural management more organized, efficient, and accessible through technology.

The system provides a digital platform where farmers can manage their farms, fields, crops, planting cycles, farming activities, and expenses. It also includes an administrative dashboard that allows administrators to monitor registered farmers and view agricultural information.

The main goal of this project is to support data-driven agricultural management and improve the organization of farming activities.

## 🎯 Project Objectives

- Digitize traditional farm management activities.
- Help farmers organize farm and field information.
- Track crop cultivation and planting cycles.
- Record farming activities and agricultural expenses.
- Generate reports for better agricultural decision-making.
- Provide administrators with centralized farmer management.
- Support more efficient and organized agricultural operations.

##  Key Features

### 👨‍🌾 Farmer Panel

- Farmer Registration and Login
- Secure Authentication
- Farmer Dashboard
- Farm Management
- Field Management
- Crop Management
- Planting Cycle Management
- Farming Activity Tracking
- Expense Management
- Agricultural Reports
- Date-Based Report Filtering
- PDF Report Export through Browser Print

### 🛡️ Admin Panel

- Admin Login
- Admin Dashboard
- Total Farmers Overview
- Total Farms Overview
- Total Fields Overview
- Total Crops Overview
- Registered Farmer Management
- Farmer Search Functionality
- Individual Farmer Details
- Farm and Field Information
- Agricultural Statistics

### 📊 Reporting and Analytics

- Expense Summary
- Expense Category Analysis
- Monthly Expense Analysis
- Crop-Based Reports
- Farm-Based Reports
- Date-Based Filtering

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python |
| Frontend | HTML, CSS, JavaScript |
| Database | MySQL |
| Database Tool | MySQL Workbench |
| Backend Server | Python HTTPServer |
| Authentication | Session-Based Authentication |
| Password Security | PBKDF2-SHA256 |
| Development Environment | Visual Studio Code |

**Note:** The project uses Python's built-in HTTP server and does not depend on Flask, Django, or FastAPI.

## 🏗️ System Architecture

The application follows a simple client-server architecture.

1. The frontend provides the user interface.
2. JavaScript communicates with the backend through API endpoints.
3. The Python backend handles authentication, business logic, and requests.
4. MySQL stores farmer, farm, field, crop, activity, and expense information.
5. The backend returns data to the frontend in JSON format.

## 📂 Project Structure

```text
SMART_AGRICULTURE/
│
├── backend/
│   ├── server.py
│   ├── database.py
│   ├── farmer.py
│   ├── admin.py
│   ├── password_utils.py
│   └── create_admin.py
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── main.js
│   │
│   ├── admin.html
│   ├── admin-dashboard.html
│   └── [Other Farmer Panel Pages]
│
├── database/
│   └── [Database SQL Scripts]
│
├── README.md
└── requirements.txt
```

*The structure above is a documentation example. Update it according to the actual files in your repository.*

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/smart-agriculture-crop-management.git
```

### 2. Navigate to the Project Directory

```bash
cd smart-agriculture-crop-management
```

### 3. Install Dependencies

```bash
pip install mysql-connector-python
```

### 4. Configure MySQL Database

- Open MySQL Workbench.
- Create a database named `smart_agriculture_db`.
- Configure your MySQL connection credentials in the backend database configuration.
- Import or execute the project's database SQL scripts if provided.

### 5. Run the Application

```bash
python backend/server.py
```

### 6. Open in Browser

```text
http://127.0.0.1:8000
```

## 🔐 Security

The project includes:

- Password hashing using PBKDF2-SHA256.
- Session-based authentication.
- Separate farmer and administrator authentication.
- Protected backend API endpoints.
- Role-based access checks.

## 🚀 Future Improvements

- Unified Login System for Farmers and Administrators.
- Weather-Based Agricultural Insights.
- Advanced Crop Recommendation System.
- AI-Based Crop Disease Detection.
- Smart Irrigation Recommendations.
- Advanced Agricultural Data Visualization.
- Mobile-Friendly User Experience.


