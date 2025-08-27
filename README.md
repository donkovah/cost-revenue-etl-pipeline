# 🚚 Cost-Revenue ETL Pipeline

A modern, domain-driven ETL pipeline for processing shipping cost and revenue data with automated validation, transformation, and S3 storage integration.

## 📊 **Project Overview**

This project implements an enterprise-grade ETL pipeline that:
- **Extracts** shipping data from CSV files
- **Transforms** raw data using business logic and validation
- **Loads** processed data to AWS S3 with proper partitioning
- **Validates** data at multiple layers (input, business rules, schema)
- **Calculates** derived business metrics (profit, margins, shipping duration)
- **Provides** analytics and business intelligence capabilities

## 🏗️ **Architecture**

Built following **Domain-Driven Design (DDD)** and **Clean Architecture** principles:

```
src/
├── 🎯 domain/                     # Business Logic Layer
│   ├── models/
│   │   └── shipment.py           # Core business entity
│   ├── interfaces/               # Contracts (5 separate files)
│   │   ├── repository.py         # Data access contracts
│   │   ├── storage.py            # File storage contracts
│   │   ├── validator.py          # Validation contracts
│   │   ├── notification.py       # Notification contracts
│   │   └── metrics.py            # Metrics contracts
│   └── services/                 # Business orchestration
│       ├── etl_service.py        # ETL pipeline logic
│       └── analytics_service.py  # Business intelligence
├── 🔧 infra/                     # Infrastructure Layer
│   └── adapters/                 # Interface implementations
│       ├── s3_storage_adapter.py        # AWS S3 operations
│       ├── csv_repository_adapter.py    # CSV data handling
│       ├── pandera_validator_adapter.py # Schema validation
│       ├── console_notification_adapter.py # Logging
│       └── simple_metrics_adapter.py    # Metrics collection
└── 🚀 app/                       # Application Layer
    ├── cli.py                    # Command-line interface
    ├── config.py                 # Configuration management
    └── services/
        └── etl.py               # Legacy compatibility layer
```

## ✨ **Key Features**

### 🔄 **ETL Pipeline**
- **Robust Data Processing**: Handles missing data, type conversions, date parsing
- **Business Logic Integration**: Automatic calculation of profits, margins, shipping duration
- **Multi-Layer Validation**: Input validation, business rules, schema compliance
- **Error Handling**: Comprehensive error reporting and recovery mechanisms

### 📊 **Business Intelligence**
- **Profitability Analysis**: Identifies profitable vs. unprofitable shipments
- **Performance Metrics**: Shipping duration analysis, delay identification
- **Margin Analysis**: High-margin shipment identification
- **Route Optimization**: Geographic and route-based insights

### 🛡️ **Data Quality**
- **Schema Validation**: Using Pandera for robust data validation
- **Business Rule Enforcement**: Domain-specific constraints and invariants
- **Data Integrity**: Multi-layer validation ensuring data quality
- **Audit Trail**: Comprehensive logging and metrics collection

### ☁️ **Cloud Integration**
- **AWS S3 Storage**: Automated upload with date partitioning
- **Multiple Formats**: CSV and Parquet support for different use cases
- **LocalStack Support**: Local development environment

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.11+
- Poetry (for dependency management)
- Docker & Docker Compose (for LocalStack)
- AWS CLI (optional, for production S3)

### **Installation**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd cost-revenue-etl-pipeline
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start LocalStack (for local development):**
   ```bash
   docker-compose up -d
   ```

### **Environment Configuration**

Create a `.env` file with:

```env
# Data Source
CSV_FILE_PATH=./data-source.csv

# AWS Configuration
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
AWS_ENDPOINT_URL=http://localhost:4566

# S3 Configuration
S3_BUCKET_NAME=cost-revenue-bucket
```

## 🎯 **Usage**

### **Command Line Interface**

Run the complete ETL pipeline:

```bash
# Activate poetry environment
poetry shell

# Run the ETL pipeline
python -m src.app.cli
```

### **Programmatic Usage**

```python
from src.domain.services import ShipmentETLService
from src.infra.adapters import (
    S3StorageAdapter, 
    CSVShipmentRepository, 
    PanderaDataValidator
)

# Initialize services with dependency injection
etl_service = ShipmentETLService(
    repository=CSVShipmentRepository(),
    storage_service=S3StorageAdapter(),
    validator=PanderaDataValidator()
)

# Process shipments
result = etl_service.process_shipments('data.csv', 'my-bucket')
```

### **Legacy Compatibility**

For backward compatibility with existing code:

```python
from src.app.services.etl import run_etl_pipeline

# Legacy function that delegates to new architecture
result = run_etl_pipeline('data.csv', 'my-bucket')
```

## 📊 **Data Schema**

### **Input CSV Format**
```csv
guid,origin,destination,cost,revenue,shipping_date,delivery_date
ABC123-DEF-456,New York,Los Angeles,1200.50,1800.00,2024-01-15,2024-01-18
```

### **Output Schema**
Enhanced with calculated fields:
```json
{
  "guid": "ABC123-DEF-456",
  "origin": "New York",
  "destination": "Los Angeles", 
  "cost": 1200.50,
  "revenue": 1800.00,
  "shipping_date": "2024-01-15",
  "delivery_date": "2024-01-18",
  "profit": 599.50,
  "profit_margin": 33.31,
  "shipping_duration_days": 3,
  "processed_at": "2024-01-20T10:30:00",
  "year": 2024,
  "month": 1,
  "quarter": 1
}
```

## 🔍 **Business Metrics**

The pipeline automatically calculates:

- **💰 Profit**: `revenue - cost`
- **📈 Profit Margin**: `(profit / revenue) * 100`
- **⏱️ Shipping Duration**: Days between shipping and delivery
- **🎯 Business Classifications**:
  - `is_profitable`: Profit > 0
  - `is_high_margin`: Profit margin > 20%
  - `is_delayed`: Shipping duration > 7 days

## 🧪 **Testing**

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/test_shipment.py
```

## 📈 **Analytics Capabilities**

### **Route Analysis**
```python
from src.domain.services import ShipmentAnalyticsService

analytics = ShipmentAnalyticsService(repository)
route_analysis = analytics.analyze_routes(shipments)
```

### **Performance Insights**
- Most profitable routes
- Average shipping durations by route
- Delay pattern analysis
- Cost optimization recommendations

## 🔧 **Development**

### **Adding New Features**

1. **Domain First**: Define business logic in `domain/models/`
2. **Interface Definition**: Create contracts in `domain/interfaces/`
3. **Implementation**: Add adapters in `infra/adapters/`
4. **Integration**: Wire up in `app/` layer

### **Architecture Principles**

- **🎯 Domain-Driven Design**: Business logic is central and independent
- **🔄 Dependency Inversion**: Domain defines contracts, infrastructure implements
- **🧩 Single Responsibility**: Each class/module has one clear purpose
- **🧪 Testability**: Easy mocking through interfaces
- **🔧 Maintainability**: Clean separation of concerns

## 📝 **Configuration Management**

Centralized configuration in `src/app/config.py`:
- Environment variable loading
- Validation of required settings
- Default value management
- Type safety with Pydantic

## 📊 **Monitoring & Observability**

### **Metrics Collection**
- Pipeline execution metrics
- Data quality metrics
- Business performance indicators
- Error rate tracking

### **Logging**
- Structured logging throughout the pipeline
- Different log levels for different environments
- Audit trail for data processing

## 🚀 **Deployment**

### **Docker Support**
```bash
# Build the image
docker build -t cost-revenue-etl .

# Run with Docker Compose
docker-compose up
```

### **Production Considerations**
- Use real AWS S3 instead of LocalStack
- Configure proper IAM roles and permissions
- Set up monitoring and alerting
- Implement data backup strategies

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow the existing architecture patterns
4. Add tests for new functionality
5. Ensure all tests pass: `poetry run pytest`
6. Submit a pull request

## 📚 **Documentation**

- **[Architecture Guide](ARCHITECTURE.md)**: Detailed architectural decisions
- **[API Documentation](docs/api.md)**: Service interfaces and contracts
- **[Business Rules](docs/business-rules.md)**: Domain logic documentation

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 **Project Status**

✅ **Completed Features:**
- Domain-driven architecture implementation
- Multi-layer validation system
- AWS S3 integration with LocalStack
- Business intelligence analytics
- Comprehensive error handling
- Metrics and monitoring

🚧 **Future Enhancements:**
- Web API interface
- Real-time streaming support
- Advanced analytics dashboard
- Multi-format data source support
- Automated data quality reporting

---

**Built with 💙 using Domain-Driven Design principles and Clean Architecture patterns.**
