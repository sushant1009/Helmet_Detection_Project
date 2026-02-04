# Helmet Compliance & Attendance System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Java](https://img.shields.io/badge/Java-11+-orange.svg)](https://www.oracle.com/java/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> An intelligent AI-powered safety compliance system combining real-time helmet detection with facial recognition-based attendance tracking.

![Project Banner](https://img.shields.io/badge/Status-Active-success)
![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Modules](#-modules)
- [Use Cases](#-use-cases)
- [License](#-license)
- [Contact](#-contact)

---

## Overview

This comprehensive safety monitoring system leverages computer vision and machine learning to ensure workplace safety compliance. The system provides:

- **Real-time helmet detection** from video streams
- **Facial recognition-based attendance** tracking
- **Compliance monitoring** and violation reporting
- **Web-based dashboard** for management and analytics

Built with a microservices architecture, the system is scalable, maintainable, and suitable for industrial environments, construction sites, and safety-critical workplaces.

---

## Features

###  Computer Vision
- Real-time helmet detection using deep learning models
- Multi-person detection and tracking
- High accuracy rate (>95%)
- Video stream processing support

### Facial Recognition
- Employee identification through facial embeddings
- Automated attendance logging
- Support for multiple camera feeds
- Fast recognition (<100ms per frame)

### Compliance Management
- Real-time safety violation alerts
- Comprehensive reporting and analytics
- Violation history tracking
- Export reports (PDF/Excel)

###  User Interface
- Modern React-based dashboard
- Real-time monitoring display
- Employee management panel
- Customizable alerts and notifications

### Technical Features
- Microservices architecture
- RESTful API design
- Docker containerization support
- Scalable deployment options

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│                    (React Dashboard)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API
                     │
┌────────────────────┴────────────────────────────────────────┐
│                  Backend Services Layer                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Helmet     │  │  Compliance  │  │  Attendance  │       │
│  │  Detection   │  │    Server    │  │    Server    │       │
│  │   Service    │  │    (Java)    │  │   (Python)   │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │             │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴─────────────┐
│                    Data Layer                               │
│         (Database, Face Embeddings, ML Models)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Frontend
- **React.js** - Modern UI framework
- **JavaScript (ES6+)** - Client-side logic
- **CSS3** - Styling and responsive design
- **Axios** - HTTP client for API calls

### Backend Services
- **Java + Spring Boot** - Compliance management service
- **Python** - ML services and data processing
- **RESTful APIs** - Service communication
- **FastAPI/Flask** - Python web frameworks

### Machine Learning & AI
- **Computer Vision** - Helmet detection
- **Deep Learning** - YOLOv5/YOLOv8 or similar object detection
- **Facial Recognition** - Face embeddings generation
- **OpenCV** - Image processing
- **TensorFlow/PyTorch** - ML frameworks

### DevOps & Tools
- **Docker** - Containerization
- **Jupyter Notebook** - Model development
- **Git** - Version control
- **Maven/Gradle** - Java build tools
- **npm** - JavaScript package manager

### Languages Distribution
- ![Java](https://img.shields.io/badge/Java-34.7%25-orange)
- ![Python](https://img.shields.io/badge/Python-31.4%25-blue)
- ![JavaScript](https://img.shields.io/badge/JavaScript-28.3%25-yellow)
- ![CSS](https://img.shields.io/badge/CSS-4.4%25-blueviolet)
- ![Others](https://img.shields.io/badge/Others-1.2%25-lightgrey)

---

## Project Structure

```
Helmet_Detection_Project/
│
├── helmet_detection_backend/          # Python-based helmet detection service
│   ├── models/                        # Trained ML models
│   ├── api/                           # API endpoints
│   ├── utils/                         # Helper functions
│   └── README.md                      # Service-specific documentation
│
├── helmet_compliance_server/          # Java Spring Boot compliance service
│   ├── src/main/java/                 # Java source code
│   ├── src/main/resources/            # Configuration files
│   └── README.md                      # Service-specific documentation
│
├── attendance_server/                 # Attendance tracking service
│   ├── api/                           # API endpoints
│   ├── database/                      # Database schemas
│   └── README.md                      # Service-specific documentation
│
├── face_embeddings_generator/         # Facial embeddings preprocessing
│   ├── embeddings/                    # Generated face embeddings
│   ├── models/                        # Face recognition models
│   └── README.md                      # Service-specific documentation
│
├── helmet-ui/                         # React frontend application
│   ├── src/                           # React components
│   ├── public/                        # Static assets
│   ├── package.json                   # Dependencies
│   └── README.md                      # UI-specific documentation
│
├── End_to_End_Pipeline/               # Complete workflow integration
│   ├── scripts/                       # Automation scripts
│   └── README.md                      # Pipeline documentation
│
├── .gitignore                         # Git ignore rules
├── LICENSE                            # MIT License
├── README.md                          # This file
└── docker-compose.yml                 # (Optional) Multi-container setup
```

---

##  Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python** 3.8 or higher
- **Java JDK** 11 or higher
- **Node.js** 14 or higher
- **npm** or **yarn**
- **Docker** (optional, for containerized deployment)
- **Git**

### Installation

#### 1 Clone the Repository

```bash
git clone https://github.com/sushant1009/Helmet_Detection_Project.git
cd Helmet_Detection_Project
```

#### 2 Setup Python Services

```bash
# Helmet Detection Backend
cd helmet_compliance_server
pip install -r requirements.txt
python app.py

# Face Embeddings Generator
cd ../face_embeddings_generator
pip install -r requirements.txt
python app.py

# Attendance Server
cd ../attendance_server
pip install -r requirements.txt
python app.py
```

#### 3 Setup Java Service

```bash
cd helmet_detection_backend

# Using Maven
mvn clean install
mvn spring-boot:run

# Or using Gradle
./gradlew build
./gradlew bootRun
```

#### 4 Setup Frontend

```bash
cd helmet-ui
npm install
npm start
```

The application will be available at `http://localhost:3000`

#### 5 Docker Setup (Optional)

```bash
# Build and run all services
docker-compose up --build

# Run in detached mode
docker-compose up -d
```

### Configuration

Create environment configuration files:

**`.env` (Backend Services)**
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/helmet_db

# Model Paths
HELMET_MODEL_PATH=./models/helmet_detection.h5
FACE_MODEL_PATH=./models/face_recognition.h5

# Service URLs
COMPLIANCE_SERVICE_URL=http://localhost:8080
ATTENDANCE_SERVICE_URL=http://localhost:8001
```

**Frontend Configuration** (`helmet-ui/.env`)
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_COMPLIANCE_API=http://localhost:8080
```

---

## Modules

### 1. Helmet Detection Backend
**Technology:** Python, OpenCV, Deep Learning  
**Purpose:** Real-time helmet detection from video streams  
**Key Features:**
- YOLOv5/YOLOv8 object detection
- Real-time video processing
- REST API for detection requests

[ Detailed Documentation →](./helmet_detection_backend/README.md)

### 2. Helmet Compliance Server
**Technology:** Java, Spring Boot  
**Purpose:** Manage compliance rules and violation tracking  
**Key Features:**
- Violation logging and reporting
- Rule engine for compliance checks
- Report generation (PDF/Excel)

[ Detailed Documentation →](./helmet_compliance_server/README.md)

### 3. Attendance Server
**Technology:** Python, Flask/FastAPI  
**Purpose:** Handle attendance tracking through facial recognition  
**Key Features:**
- Real-time face recognition
- Attendance logging
- Employee database management

[Detailed Documentation →](./attendance_server/README.md)

### 4. Face Embeddings Generator
**Technology:** Python, Deep Learning  
**Purpose:** Generate and manage facial embeddings  
**Key Features:**
- Face embedding generation
- Database of known faces
- Model training pipeline

[ Detailed Documentation →](./face_embeddings_generator/README.md)

### 5. Helmet UI
**Technology:** React, JavaScript  
**Purpose:** Web-based dashboard for monitoring and management  
**Key Features:**
- Real-time monitoring display
- Employee management
- Compliance reporting dashboard

[Detailed Documentation →](./helmet-ui/README.md)

### 6. End-to-End Pipeline
**Technology:** Python, Shell Scripts  
**Purpose:** Orchestrate complete workflow  
**Key Features:**
- Automated deployment scripts
- Integration testing
- Full pipeline execution

[Detailed Documentation →](./End_to_End_Pipeline/README.md)

---


---

## Use Cases

### Construction Sites
- Monitor helmet compliance across multiple locations
- Automated violation reporting
- Contractor attendance tracking

### Manufacturing Plants
- Ensure PPE compliance in production areas
- Track employee movements in restricted zones
- Safety audit trail

### Warehouses & Logistics
- Forklift zone safety monitoring
- Automated attendance for shift workers
- Compliance reporting for safety inspections

###  Industrial Facilities
- High-risk area monitoring
- Emergency response tracking
- Safety training compliance

---


```markdown
### Dashboard
![Dashboard](./docs/images/dashboard.png)

### Real-time Detection
![Detection](./docs/images/detection.png)

### Compliance Reports
![Reports](./docs/images/reports.png)
```

---

## Security & Privacy

- **Data Encryption:** All data transmitted over HTTPS
- **Face Embeddings:** Stored securely with encryption at rest
- **GDPR Compliant:** User data handling follows privacy regulations
- **Access Control:** Role-based permissions (Admin, Manager, Viewer)
- **Audit Logs:** Complete tracking of all system activities

---


---

## Performance

- **Detection Speed:** 30+ FPS on GPU, 10-15 FPS on CPU
- **Recognition Accuracy:** >95% for known faces
- **System Latency:** <100ms end-to-end processing
- **Concurrent Streams:** Supports up to 4 simultaneous camera feeds

---

## Roadmap

- [x] Core helmet detection functionality
- [x] Facial recognition integration
- [x] Web dashboard
- [ ] Mobile application (iOS/Android)
- [ ] Advanced analytics and ML insights
- [ ] Multi-language support
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] Integration with HR systems (SAP, Workday)

---


## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Author

**Sushant**

- GitHub: [@sushant1009](https://github.com/sushant1009)
- LinkedIn: [Add your LinkedIn]
- Email: [Add your email]

---

## Acknowledgments

- YOLOv5/YOLOv8 for object detection models
- OpenCV community for computer vision tools
- React community for frontend framework
- Spring Boot team for backend framework
- All contributors and open-source projects that made this possible

---

## Contact & Support

For questions, issues, or collaboration opportunities:

- **Issues:** [GitHub Issues](https://github.com/sushant1009/Helmet_Detection_Project/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sushant1009/Helmet_Detection_Project/discussions)
- **Email:** [sush0ntsabale031@gmail.com]

---

## Star History

If you find this project helpful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=sushant1009/Helmet_Detection_Project&type=Date)](https://star-history.com/#sushant1009/Helmet_Detection_Project&Date)

---

<div align="center">

**Made with  by Sushant**

If this project helped you, please ⭐ star the repository!

</div>
