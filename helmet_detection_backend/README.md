# Helmet Detection Backend

Spring Boot orchestration service that coordinates helmet detection workflow by integrating face embeddings, attendance tracking, and compliance management services.

## Overview

This Spring Boot service acts as the central orchestrator for the helmet detection system. It doesn't perform ML operations directly but coordinates between multiple microservices to achieve complete helmet safety monitoring workflow:

- Calls **Face Embeddings Generator** for facial recognition
- Integrates with **Attendance Server** for employee check-in/out
- Updates **Helmet Compliance Server** with violation records
- Provides unified REST API for frontend applications

## 🛠️ Tech Stack

- **Java 11+**
- **Spring Boot 2.7+**
- **Spring Web** - REST API
- **Spring WebClient/RestTemplate** - HTTP client for service calls
- **Spring Cloud (Optional)** - Service discovery
- **Lombok** - Reduce boilerplate
- **Maven/Gradle** - Build tool
- **MySQL/PostgreSQL** - Database (optional for caching/logs)

## Architecture Role

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API
                     │
┌────────────────────▼────────────────────────────────────────┐
│         Helmet Detection Backend (THIS SERVICE)             │
│              Spring Boot Orchestrator                       │
└─────┬──────────────┬──────────────────┬─────────────────────┘
      │              │                  │
      │              │                  │
      ▼              ▼                  ▼
┌───────────┐  ┌──────────────┐  ┌─────────────────┐
│  Face     │  │  Attendance  │  │    Helmet       │
│Embeddings │  │   Server     │  │  Compliance     │
│Generator  │  │  (Python)    │  │    Server       │
│ (Python)  │  └──────────────┘  │    (Python)     │
└───────────┘                    └─────────────────┘
```

## Installation

### Prerequisites
- Java JDK 11 or higher
- Maven 3.6+ or Gradle 7+
- Access to Face Embeddings Generator service
- Access to Attendance Server
- Access to Helmet Compliance Server

### Setup

```bash
# Navigate to the service directory
cd helmet_detection_backend

# Build with Maven
mvn clean install

# Or build with Gradle
./gradlew build
```

## Configuration

Edit `src/main/resources/application.properties`:

```properties
# Server Configuration
server.port=8081
spring.application.name=helmet-detection-backend

# External Service URLs
service.embeddings.url=http://localhost:8000
service.attendance.url=http://localhost:8001
service.compliance.url=http://localhost:8080

# Connection Timeouts
service.connection.timeout=5000
service.read.timeout=10000

# Database (Optional - for logging/caching)
spring.datasource.url=jdbc:mysql://localhost:3306/helmet_detection
spring.datasource.username=your_username
spring.datasource.password=your_password
spring.jpa.hibernate.ddl-auto=update

# Logging
logging.level.root=INFO
logging.level.com.helmet.detection=DEBUG

# CORS Configuration
cors.allowed.origins=http://localhost:5000
```

Or use `application.yml`:

```yaml
server:
  port: 8081

spring:
  application:
    name: helmet-detection-backend

service:
  embeddings:
    url: http://localhost:8000
  attendance:
    url: http://localhost:8001
  compliance:
    url: http://localhost:8080
  connection:
    timeout: 5000
  read:
    timeout: 10000

logging:
  level:
    root: INFO
    com.helmet.detection: DEBUG
```

## 🚀 Usage

### Running the Service

```bash
# Maven
mvn spring-boot:run

# Gradle
./gradlew bootRun

# Run JAR directly
java -jar target/helmet-detection-backend-1.0.0.jar
```

### Docker

```bash
# Build image
docker build -t helmet-detection-backend .

# Run container
docker run -p 8081:8081 \
  -e SERVICE_EMBEDDINGS_URL=https://huggingface.co/spaces/Sushant1004/Face-Embeddings-Generator/ \
  -e SERVICE_ATTENDANCE_URL=http://attendance:8001 \
  -e SERVICE_COMPLIANCE_URL=http://compliance:8080 \
  helmet-detection-backend
```

## 📡 API Endpoints

### 1. Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "UP",
  "services": {
    "embeddings": "UP",
    "attendance": "UP",
    "compliance": "UP"
  }
}
```

### 2. Process Detection Event

```http
POST /api/v1/detection/process
Content-Type: application/json
```

**Request Body:**
```json
{
  "image": "base64_encoded_image",
  "cameraId": "CAM_01",
  "location": "Zone A - Entry Gate",
  "timestamp": "2025-02-04T10:30:00Z"
}
```

**Response:**
```json
{
  "processId": "PROC_12345",
  "detections": [
    {
      "personId": "P001",
      "hasHelmet": false,
      "confidence": 0.95,
      "employeeId": "EMP001",
      "employeeName": "John Doe",
      "attendanceMarked": true,
      "violationLogged": true
    }
  ],
  "summary": {
    "totalPersons": 1,
    "compliant": 0,
    "nonCompliant": 1,
    "attendanceRecords": 1,
    "violations": 1
  },
  "timestamp": "2025-02-04T10:30:05Z"
}
```

### 3. Mark Attendance with Face Recognition

```http
POST /api/v1/attendance/mark-attendance
Content-Type: application/json
```

**Request Body:**
```json
{
  "image": "base64_encoded_face_image",
  "cameraId": "CAM_ENTRY",
  "timestamp": "2025-02-04T09:00:00Z"
}
```

**Workflow:**
1. Calls **Face Embeddings Generator** to extract face embeddings & save Embedding in MongoDB
2. Calls **Attendance Server** to identify employee and mark attendance
3. Returns consolidated response

**Response:**
```json
{
  "success": true,
  "employeeId": "EMP001",
  "employeeName": "John Doe",
  "department": "Engineering",
  "checkInTime": "2025-02-04T09:00:00Z",
  "recognitionConfidence": 0.98,
  "status": "CHECKED_IN"
}
```

### 4. Log Helmet Violation

```http
POST /api/v1/violations/log
Content-Type: application/json
```

**Request Body:**
```json
{
  "employeeId": "EMP002",
  "image": "base64_encoded_image",
  "cameraId": "CAM_01",
  "location": "Zone A",
  "detectionConfidence": 0.93,
  "timestamp": "2025-02-04T11:15:00Z"
}
```

**Workflow:**
1. Extracts employee info (optionally calls embeddings service for face ID)
2. Calls **Helmet Compliance Server** to create violation record
3. Returns violation details

**Response:**
```json
{
  "violationId": 1234,
  "employeeId": "EMP002",
  "employeeName": "Jane Smith",
  "violationType": "NO_HELMET",
  "severity": "HIGH",
  "status": "OPEN",
  "imageUrl": "/violations/img_1234.jpg",
  "timestamp": "2025-02-04T11:15:00Z"
}
```

### 5. Get Employee Info with Face Recognition

```http
POST /api/v1/employee/identify
Content-Type: application/json
```

**Request Body:**
```json
{
  "faceImage": "base64_encoded_face_image"
}
```

**Workflow:**
1. Calls **Face Embeddings Generator** to extract embeddings
2. Calls **Attendance Server** to identify employee
3. Returns employee details

**Response:**
```json
{
  "identified": true,
  "employeeId": "EMP001",
  "name": "John Doe",
  "department": "Engineering",
  "confidence": 0.97
}
```

## 🔄 Service Integration Flow

### Complete Detection Workflow

```java
1. Frontend sends image to /api/v1/detection/process

2. Backend orchestrates:
   ┌─────────────────────────────────────┐
   │ Step 1: Extract Face Embeddings     │
   │ → Call Face Embeddings Generator    │
   └─────────────────┬───────────────────┘
                     │
   ┌─────────────────▼───────────────────┐
   │ Step 2: Identify Employee           │
   │ → Call Attendance Server            │
   │ → Mark attendance if needed         │
   └─────────────────┬───────────────────┘
                     │
   ┌─────────────────▼───────────────────┐
   │ Step 3: Check Helmet Compliance     │
   │ → If no helmet detected             │
   │ → Call Compliance Server            │
   │ → Log violation                     │
   └─────────────────┬───────────────────┘
                     │
                     ▼
   Return consolidated response to Frontend
```

## 📁 Project Structure

```
helmet_detection_backend/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/helmet/detection/
│   │   │       ├── controller/
│   │   │       │   ├── DetectionController.java
│   │   │       │   ├── AttendanceController.java
│   │   │       │   └── ViolationController.java
│   │   │       ├── service/
│   │   │       │   ├── OrchestrationService.java
│   │   │       │   ├── EmbeddingsServiceClient.java
│   │   │       │   ├── AttendanceServiceClient.java
│   │   │       │   └── ComplianceServiceClient.java
│   │   │       ├── dto/
│   │   │       │   ├── DetectionRequest.java
│   │   │       │   ├── DetectionResponse.java
│   │   │       │   ├── AttendanceRequest.java
│   │   │       │   └── ViolationRequest.java
│   │   │       ├── config/
│   │   │       │   ├── WebClientConfig.java
│   │   │       │   ├── RestTemplateConfig.java
│   │   │       │   └── CorsConfig.java
│   │   │       ├── exception/
│   │   │       │   ├── ServiceUnavailableException.java
│   │   │       │   └── GlobalExceptionHandler.java
│   │   │       └── DetectionBackendApplication.java
│   │   └── resources/
│   │       ├── application.properties
│   │       ├── application-dev.properties
│   │       └── application-prod.properties
│   └── test/
│       └── java/
│           └── com/helmet/detection/
│               ├── controller/
│               ├── service/
│               └── integration/
├── pom.xml  # Maven
├── build.gradle  # Gradle
├── Dockerfile
└── README.md
```

## 🔧 Key Components

### 1. OrchestrationService

```java
@Service
@RequiredArgsConstructor
public class OrchestrationService {
    
    private final EmbeddingsServiceClient embeddingsClient;
    private final AttendanceServiceClient attendanceClient;
    private final ComplianceServiceClient complianceClient;
    
    public DetectionResponse processDetection(DetectionRequest request) {
        // 1. Extract face embeddings
        FaceEmbedding embedding = embeddingsClient.extractEmbeddings(request.getImage());
        
        // 2. Identify employee and mark attendance
        EmployeeInfo employee = attendanceClient.identifyAndMarkAttendance(embedding);
        
        // 3. Check helmet compliance
        if (!request.isHelmetDetected()) {
            complianceClient.logViolation(employee.getId(), request);
        }
        
        return buildResponse(employee, request);
    }
}
```

### 2. Service Clients

```java
@Service
@RequiredArgsConstructor
public class EmbeddingsServiceClient {
    
    @Value("${service.embeddings.url}")
    private String embeddingsServiceUrl;
    
    private final WebClient webClient;
    
    public FaceEmbedding extractEmbeddings(String image) {
        return webClient.post()
            .uri(embeddingsServiceUrl + "/api/embeddings/extract")
            .bodyValue(Map.of("image", image))
            .retrieve()
            .bodyToMono(FaceEmbedding.class)
            .block();
    }
}
```

## 📦 Dependencies

Key dependencies in `pom.xml`:

```xml
<dependencies>
    <!-- Spring Boot Starter Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- Spring Boot WebFlux (for WebClient) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-webflux</artifactId>
    </dependency>
    
    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
    </dependency>
    
    <!-- Spring Boot Actuator (Health checks) -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    
    <!-- Optional: Spring Cloud (for service discovery) -->
    <dependency>
        <groupId>org.springframework.cloud</groupId>
        <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
    </dependency>
    
    <!-- Optional: Resilience4j (Circuit breaker) -->
    <dependency>
        <groupId>io.github.resilience4j</groupId>
        <artifactId>resilience4j-spring-boot2</artifactId>
    </dependency>
</dependencies>
```

## 🧪 Testing

```bash
# Run all tests
mvn test

# Run integration tests
mvn verify

# Run with coverage
mvn test jacoco:report

# Test specific class
mvn test -Dtest=OrchestrationServiceTest
```

## 🔐 Security

- **API Key Authentication** for service-to-service calls
- **JWT Tokens** for frontend authentication
- **CORS Configuration** for web access
- **Rate Limiting** to prevent abuse
- **Input Validation** on all endpoints

## 📊 Error Handling

### Service Unavailability

```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ServiceUnavailableException.class)
    public ResponseEntity<ErrorResponse> handleServiceUnavailable(ServiceUnavailableException ex) {
        return ResponseEntity
            .status(HttpStatus.SERVICE_UNAVAILABLE)
            .body(new ErrorResponse(
                "SERVICE_UNAVAILABLE",
                ex.getMessage(),
                LocalDateTime.now()
            ));
    }
}
```

### Retry Logic

```java
@Retryable(
    value = {WebClientRequestException.class},
    maxAttempts = 3,
    backoff = @Backoff(delay = 1000)
)
public FaceEmbedding extractEmbeddings(String image) {
    // Service call with automatic retry
}
```

## 📈 Performance Optimization

- **Connection Pooling** for HTTP clients
- **Async Processing** for non-blocking calls
- **Caching** frequently accessed data
- **Circuit Breaker** pattern for fault tolerance
- **Request Batching** when possible

## 🔄 Circuit Breaker Configuration

```yaml
resilience4j:
  circuitbreaker:
    instances:
      embeddingsService:
        registerHealthIndicator: true
        slidingWindowSize: 10
        minimumNumberOfCalls: 5
        permittedNumberOfCallsInHalfOpenState: 3
        waitDurationInOpenState: 10s
        failureRateThreshold: 50
```

## 🐛 Troubleshooting

**Service Connection Timeout:**
```bash
# Increase timeout in application.properties
service.connection.timeout=10000
service.read.timeout=20000
```

**Service Unavailable:**
```bash
# Check if dependent services are running
curl http://localhost:5000/health  # Embeddings
curl http://localhost:5001/health  # Attendance
curl http://localhost:8080/health  # Compliance
```

**Port Already in Use:**
```bash
# Change port in application.properties
server.port=8082
```

## 🚀 Deployment

### Environment Variables

```bash
export SERVICE_EMBEDDINGS_URL=http://embeddings-service:5000
export SERVICE_ATTENDANCE_URL=http://attendance-service:5001
export SERVICE_COMPLIANCE_URL=http://compliance-service:8080
export SERVER_PORT=8081
```

### Docker Compose Integration

```yaml
version: '3.8'
services:
  detection-backend:
    build: ./helmet_detection_backend
    ports:
      - "8081:8081"
    environment:
      - SERVICE_EMBEDDINGS_URL=http://embeddings:5000
      - SERVICE_ATTENDANCE_URL=http://attendance:5001
      - SERVICE_COMPLIANCE_URL=http://compliance:8080
    depends_on:
      - embeddings
      - attendance
      - compliance
```

## 📊 Monitoring

- **Spring Boot Actuator** endpoints for health checks
- **Prometheus** metrics integration
- **Request/Response logging**
- **Service latency tracking**

## 📝 License

This module is part of the Helmet Detection Project and follows the same MIT License.

## 👥 Contributors

See main project [README](../README.md) for contributors.

---

[← Back to Main Project](../README.md)
