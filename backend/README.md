# PraanLink Backend API

FastAPI backend for PraanLink - Your Proactive Health Companion.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Marshmallow** - Serialization/deserialization
- **python-dotenv** - Environment configuration

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Update `DATABASE_URL` with your PostgreSQL connection string
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/praanlink
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload
   ```

4. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Check-ins
- `GET /api/checkins` - Get all check-ins
- `GET /api/checkins/{id}` - Get check-in by ID
- `POST /api/checkins` - Create check-in
- `PUT /api/checkins/{id}` - Update check-in
- `DELETE /api/checkins/{id}` - Delete check-in

### Prescriptions
- `GET /api/prescriptions` - Get all prescriptions
- `GET /api/prescriptions/{id}` - Get prescription by ID
- `POST /api/prescriptions` - Create prescription
- `PUT /api/prescriptions/{id}` - Update prescription
- `DELETE /api/prescriptions/{id}` - Delete prescription

### Reports
- `GET /api/reports` - Get all reports
- `GET /api/reports/{id}` - Get report by ID
- `POST /api/reports` - Create report
- `PUT /api/reports/{id}` - Update report
- `DELETE /api/reports/{id}` - Delete report

### Hospitals
- `GET /api/hospitals` - Get all hospitals
- `GET /api/hospitals/{id}` - Get hospital by ID
- `POST /api/hospitals` - Create hospital
- `PUT /api/hospitals/{id}` - Update hospital
- `DELETE /api/hospitals/{id}` - Delete hospital

### Insurances
- `GET /api/insurances` - Get all insurances
- `GET /api/insurances/{id}` - Get insurance by ID
- `POST /api/insurances` - Create insurance
- `PUT /api/insurances/{id}` - Update insurance
- `DELETE /api/insurances/{id}` - Delete insurance

## Project Structure

```
backend/
├── db/
│   ├── database.py      # Database connection and session management
│   ├── models.py        # SQLAlchemy models
│   └── test_db.py       # Database test script
├── routers/
│   ├── checkins.py      # Check-in endpoints
│   ├── prescriptions.py # Prescription endpoints
│   ├── reports.py       # Report endpoints
│   ├── hospitals.py     # Hospital endpoints
│   └── insurances.py    # Insurance endpoints
├── main.py              # FastAPI application
├── schemas.py           # Marshmallow schemas
├── requirements.txt     # Python dependencies
└── uploads/             # File uploads directory
```

## Testing Database Connection

Run the test script:
```bash
python db/test_db.py
```

