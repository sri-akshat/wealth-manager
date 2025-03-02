# Low-Level Design (LLD) for  Backend

## 1. **Backend - Python Microservices Architecture**

### **1.1 Tech Stack**

The following technologies were chosen to optimize performance, scalability, and security for the backend:

- **Language**: Python (FastAPI for API development) – chosen for its asynchronous support, high performance, and ease of development.

- **Database**: PostgreSQL – selected for its strong ACID compliance, scalability, and support for complex queries.

- **Authentication**: JWT-based authentication with OAuth2 – provides a secure and scalable way to manage user sessions.

- **Caching**: Redis (for session management & API response caching) – speeds up API responses and reduces database load.

- **Queue Processing**: Celery + RabbitMQ (for async tasks like transaction updates) – ensures non-blocking operations and improves reliability.

- **Logging & Monitoring**: Prometheus + Grafana – enables real-time monitoring and performance tracking.

- **Deployment**: Docker + Kubernetes – allows for containerized, scalable, and automated deployments.

- **Language**: Python (FastAPI for API development) – chosen for its async support and performance.

- **Database**: PostgreSQL – provides strong ACID compliance for financial data.

- **Authentication**: JWT-based authentication with OAuth2 – ensures secure and scalable user authentication.

- **Caching**: Redis (for session management & API response caching) – improves response times for frequently accessed data.

- **Queue Processing**: Celery + RabbitMQ (for async tasks like transaction updates) – ensures non-blocking operations.

- **Logging & Monitoring**: Prometheus + Grafana – enables real-time performance tracking.

- **Deployment**: Docker + Kubernetes – ensures containerized, scalable deployment.

###

### **1.2 Database Entity Schema**

#### **User Table**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    pan VARCHAR(10) UNIQUE NOT NULL,
    kyc_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Investment Table**

```sql
CREATE TABLE investments (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    fund_name VARCHAR(255) NOT NULL,
    units DECIMAL(10,2) NOT NULL,
    investment_value DECIMAL(15,2) NOT NULL,
    current_value DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Transactions Table**

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    investment_id INT REFERENCES investments(id),
    transaction_type VARCHAR(10) CHECK (transaction_type IN ('BUY', 'SELL', 'SIP')),
    amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(20) CHECK (status IN ('Processing', 'Completed', 'Failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **KYC Table**

```sql
CREATE TABLE kyc (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    aadhaar_number VARCHAR(12) UNIQUE NOT NULL,
    pan VARCHAR(10) UNIQUE NOT NULL,
    status VARCHAR(10) CHECK (status IN ('Pending', 'Verified', 'Rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```



### 1.3 Project Structure

The project structure follows a **modular microservices approach**, ensuring **scalability** by allowing independent scaling of services based on demand. Each service is structured with clear separation of concerns, making **maintenance easier** as updates and fixes can be isolated without impacting other components. The use of a **gateway service** helps manage authentication, routing, and load balancing efficiently, ensuring smooth inter-service communication.

```plaintext
wealth-manager/
├── CONTRIBUTING.md
├── PRD.md
├── README.md
├── TRD.md
├── coverage.xml
├── docker-compose.yml
├── git-hooks/
│   └── pre-push
├── junit.xml
├── project-setup.sh
├── requirements-all.txt
├── requirements.txt
├── services/
│   ├── admin-service/
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── config/
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── api/  (Admin-specific API endpoints)
│   │   │   ├── core/ (Business logic and utilities)
│   │   │   ├── main.py (FastAPI entry point)
│   │   │   ├── models/ (Database models for admin-related entities)
│   │   │   └── schemas/ (Pydantic schemas for request/response validation)
│   │   └── tests/
│   ├── gateway/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── api/ (Gateway routing and API aggregation)
│   │   │   ├── core/ (Rate limiting, authentication handling)
│   │   │   ├── main.py (FastAPI Gateway Entry Point)
│   │   │   ├── models/ (Gateway-level configurations)
│   │   │   └── schemas/
│   ├── investment-service/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── api/ (Endpoints for investment transactions)
│   │   │   ├── core/ (Investment logic, third-party API integrations)
│   │   │   ├── models/ (Investment database models)
│   │   │   ├── schemas/ (Request/response validation)
│   │   │   ├── services/
│   │   │   │   ├── bse_mf.py (Integration with BSE MF API)
│   │   │   │   ├── mfu.py (Integration with MFU API)
│   │   │   │   ├── portfolio.py (Portfolio management logic)
│   │   │   ├── main.py
│   │   └── tests/
│   ├── kyc-service/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── api/ (KYC verification endpoints)
│   │   │   ├── core/ (Validation logic and API integrations)
│   │   │   ├── models/ (KYC entity models)
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   │   ├── aadhaar.py (Aadhaar-based verification logic)
│   │   │   │   ├── pan.py (PAN validation logic)
│   │   │   ├── main.py
│   │   └── tests/
│   ├── notification-service/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── api/ (Notification endpoints)
│   │   │   ├── core/ (SMS, email sending logic)
│   │   │   ├── models/ (Notification tracking models)
│   │   │   ├── schemas/
│   │   │   ├── main.py
│   │   └── tests/
│   ├── transaction-service/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── api/ (Transaction endpoints)
│   │   │   ├── core/ (Transaction processing logic)
│   │   │   ├── models/ (Transaction data models)
│   │   │   ├── schemas/
│   │   │   ├── main.py
│   │   └── tests/
│   ├── user-service/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── api/ (User authentication & profile management)
│   │   │   ├── core/ (User-related business logic)
│   │   │   ├── models/ (User entity models)
│   │   │   ├── schemas/
│   │   │   ├── main.py
│   │   └── tests/
├── wealth-manager.iml
```

### **1.4 API Design (Reconciled with Existing Structure)**

#### **Authentication API**

```http
POST /auth/login  # Login user & return JWT Token
Request:
{
  "email": "user@example.com",
  "password": "securepassword123"
}
Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

POST /auth/signup  # Register user & initiate KYC
Request:
{
  "email": "user@example.com",
  "password": "securepasswohn Doe",
  "pan": "ABCDE1234F"
}
Response:
{
  "message": "User registered successfully. KYC pending."
}
```

#### **Portfolio API**

```http
GET /portfolio/holdings  # Fetch Mutual Fund Holdings from CAMS/Karvy
Response:
{
  "holdings": [
    {
      "fund_name": "XYZ Bluechip Fund",
      "units": 100.5,
      "current_value": 25000.75,
      "investment_value": 20000.00
    },
    {
      "fund_name": "ABC Debt Fund",
      "units": 50.2,
      "current_value": 12000.50,
      "investment_value": 11000.00
    }
  ]
}

GET /portfolio/summary  # Show asset allocation & performance
Response:
{
  "total_investment": 31000.00,
  "current_value": 37000.25,
  "returns_percentage": 19.35
}
```

#### **Transaction API**

```http
POST /transaction/buy  # Initiate MF Purchase via BSE MF API
Request:
{
  "fund_name": "XYZ Bluechip Fund",
  "amount": 10000.00,
  "payment_method": "UPI",
  "sip": false
}
Response:
{
  "transaction_id": "TXN12345678",
  "status": "Processing"
}

POST /transaction/sell  # Redeem Units
Request:
{
  "fund_name": "XYZ Bluechip Fund",
  "units": 50.5
}
Response:
{
  "transaction_id": "TXN87654321",
  "status": "Processing"
}

POST /transaction/sip  # Start SIP Investment
Request:
{
  "fund_name": "ABC Growth Fund",
  "sip_amount": 5000.00,
  "frequency": "monthly",
  "start_date": "2025-04-01"
}
Response:
{
  "sip_id": "SIP123456",
  "status": "Active"
}
```



### **1.5 Payment & External API Integrations**

These integrations are handled as follows:

- **Synchronous APIs**: Used for immediate transaction confirmations, such as fetching live portfolio data from CAMS/Karvy and verifying KYC details through a third-party provider.

- **Asynchronous Processing**: Transactions through BSE MF/MFU APIs are processed asynchronously using Celery and RabbitMQ to handle retries, failures, and background processing, ensuring smooth user experience and resilience.

- **Webhook Support**: Payment and transaction status updates from external APIs trigger webhooks that update the system in real-time, reducing polling overhead and improving performance.

* **Batch Processing**: Large-scale data reconciliation (e.g., daily NAV updates, bulk KYC verifications) is handled using scheduled background jobs, reducing API load and optimizing resource usage.

* **BSE MF API**: Handles mutual fund transactions & payments.

* **MFU API**: Alternative mutual fund transaction API.

* **CAMS/Karvy APIs**: Fetch user holdings & portfolios.

* **KYC Provider API**: Validate Aadhaar/PAN before transactions.

### **1.6 Security Considerations**

- **Industry Compliance**: The system follows **PCI DSS** for secure financial transactions and **GDPR**/India’s **DPDP Act, 2023** for data protection, ensuring privacy and security best practices.

- **JWT Authentication**: Secure login & session management.

- **AES-256 Encryption**: Encrypt PII & sensitive data.

- **Role-Based Access Control (RBAC)**: Investors, Distributors, Admins.

- **API Rate Limiting**: Protect endpoints from abuse.

- **Compliance with Standards**: Adheres to SEBI & regulatory requirements.

