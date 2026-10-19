# DiabetesTwin API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
Currently uses simple API key in headers (for demo purposes).
```http
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-10-19T12:00:00Z",
  "models_loaded": {
    "glucose_spike": true,
    "cv_risk": true
  }
}
```

---

### Patients

#### POST /api/patients
Register a new patient.

**Request Body:**
```json
{
  "name": "John Doe",
  "age": 45,
  "gender": "M",
  "email": "john@example.com",
  "phone": "+1234567890",
  "bmi": 27.5,
  "medical_history": ["hypertension"]
}
```

**Response:**
```json
{
  "patient_id": "PAT001",
  "name": "John Doe",
  "age": 45,
  "gender": "M",
  "email": "john@example.com",
  "created_at": "2026-10-19T12:00:00Z"
}
```

#### GET /api/patients
List all patients.

**Response:**
```json
[
  {
    "patient_id": "PAT001",
    "name": "John Doe",
    "age": 45,
    "gender": "M"
  }
]
```

#### GET /api/patients/{patient_id}
Get patient details.

---

### Sensor Data

#### POST /api/patients/{patient_id}/readings
Submit sensor readings.

**Request Body:**
```json
{
  "glucose_mg_dl": 145.5,
  "heart_rate_bpm": 72,
  "steps": 5000,
  "timestamp": "2026-10-19T12:00:00Z",
  "source": "wearable"
}
```

---

### Predictions

#### POST /api/patients/{patient_id}/predict
Get health predictions.

**Request Body:**
```json
[
  {
    "glucose_mg_dl": 145.5,
    "heart_rate_bpm": 72,
    "timestamp": "2026-10-19T12:00:00Z",
    "source": "wearable"
  }
]
```

**Response:**
```json
{
  "patient_id": "PAT001",
  "spike_probability": 0.75,
  "risk_level": "HIGH",
  "recommended_actions": [
    "Take prescribed medication",
    "Increase water intake",
    "Moderate physical activity"
  ],
  "timestamp": "2026-10-19T12:00:00Z"
}
```

---

### Alerts

#### GET /api/patients/{patient_id}/alerts
Get patient alerts.

**Query Parameters:**
- `limit` (optional): Number of alerts to return (default: 10)

**Response:**
```json
[
  {
    "alert_id": "ALR001",
    "patient_id": "PAT001",
    "severity": "HIGH",
    "message": "Predicted glucose spike in 2 hours",
    "timestamp": "2026-10-19T12:00:00Z",
    "acknowledged": false
  }
]
```

#### POST /api/alerts/{alert_id}/acknowledge
Acknowledge an alert.

**Response:**
```json
{
  "alert_id": "ALR001",
  "acknowledged": true,
  "acknowledged_at": "2026-10-19T12:05:00Z"
}
```

---

### Statistics

#### GET /api/statistics
Get system statistics.

**Response:**
```json
{
  "total_patients": 100,
  "total_alerts": 250,
  "high_risk_alerts": 15,
  "timestamp": "2026-10-19T12:00:00Z"
}
```

---

### WebSocket

#### WS /ws/patient/{patient_id}
Real-time patient data streaming.

**Client Send:**
```json
{
  "type": "subscribe"
}
```

**Server Send (Prediction):**
```json
{
  "type": "prediction",
  "spike_probability": 0.75,
  "timestamp": "2026-10-19T12:00:00Z"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable