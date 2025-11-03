# PraanLink

> **🏆 Winner — Healthcare Hackathon @ IIT Bombay (organized by Loop Health)
Empathy meets intelligence — your proactive health steward walking with you every step of the way.**

PraanLink reimagines healthcare as a continuous conversation, blending empathy with intelligence. Its goal is to detect health issues before they become critical, making healthcare proactive instead of reactive.


---

## 🧠 Overview

PraanLink is a continuous-care companion that proactively manages your health journey through:

- **Continuous Care**: Regular, conversational check-ins that learn your patterns and detect anomalies early
- **Contextual Intelligence**: Analyzes your health history, reports, and conversations to spot trends before they become problems
- **Connected Ecosystem**: Bridges patients, doctors, and insurers with full context

This is not an emergency tool — it's more like a health coach that walks with you every step of the way.

---

## 🚨 The Problem

People delay seeking medical help due to:

- **Time, complexity, and language barriers** preventing access to care
- **Fragmented health data** (lab reports, prescriptions, chats) that is scattered and underused
- **No continuous health record** maintaining context across time
- **Missed early warning signs** leading to avoidable hospitalizations and costs
- **Insurance confusion** making it hard to find the right policy

---

## 💡 The Solution

PraanLink addresses these challenges through:

1. **Routine Human-like Conversations**
   - "Hey Ananya, your energy's been low this week. Shall we check your iron levels?"
   - Multilingual, empathetic, natural conversations powered by Gemini Live API

2. **Lab & Prescription Uploads**
   - Auto-parses medical documents with OCR
   - Provides insights with zero manual data entry

3. **AI-Generated Health Reports**
   - Detects trends, anomalies, and lifestyle recommendations
   - Comprehensive analysis across all health data

4. **Doctor Escalation**
   - Finds suitable doctors and books appointments
   - Sends context summaries to doctors before consultations

5. **Insurance Guidance**
   - Recommends insurance plans using embeddings + RAG-based matching
   - Personalized recommendations based on health profile

---

## ⚙️ Tech Stack

### Frontend
- **React** + **TypeScript** + **Vite** - Modern, fast development
- **Gemini Live API** + **WebSockets** - Real-time, bilingual conversations
- **shadcn/ui** + **Tailwind CSS** - Beautiful, responsive UI
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and state management

### Backend
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** + **SQLAlchemy** - Robust data storage and ORM
- **Google ADK** - Scalable orchestration of multiple AI agents
- **WhisperX** - Audio transcription and diarization
- **Uvicorn** - ASGI server

### AI Pipeline
- **Google ADK (Agent Development Kit)** - Multi-agent orchestration
- **Gemini Flash** - Medical text analysis and generation
- **Medical OCR** - Document processing
- **RAG (Retrieval-Augmented Generation)** - Insurance plan matching
- **Embeddings** - Semantic search for insurance recommendations

### Design Philosophy
Scalable, modular, and explainable — grows with your health needs.

---

## 🧩 Multi-Agent Architecture

### 1. **Multilingual Conversational Agent**
- Uses Gemini Live API + WebSockets for instant dialogue
- Retains memory and personalization
- Supports English and Hindi with natural conversation flow

### 2. **Lab Reports & Prescription Analysis Suite**
- **Lab Report Agent**: Extracts data from medical PDFs, flags abnormal parameters, calculates risk
  - Lab Parser: OCR and extraction
  - Lab Analyzer: Pattern detection
  - Lab Risk Scorer: Risk assessment
  - Lab Summarizer: Patient-friendly summaries
- **Prescription Agent**: Extracts structured prescription data, medication tracking, adherence monitoring

### 3. **Medical Report Agent**
- Synthesizes conversations + reports into structured clinical summaries
- **Timeline Builder**: Organizes health data chronologically
- **Trend Analyzer**: Detects changes in parameters over time
- **Risk Scorer**: Computes personalized health risk indices
- **Disease Inference**: Suggests possible conditions
- **Medication Aggregator**: Tracks prescription adherence & interactions
- **Patient Report Generator**: Converts data into clear summaries
- **Report Aggregator**: Creates comprehensive dossiers for doctors or insurers

### 4. **Insurance Agent**
- Uses embeddings and retrieval-augmented generation (RAG) to suggest insurance plans
- Personalized recommendations based on health profile and needs

### 5. **Core Orchestrator**
- ADK-based coordination layer for seamless inter-agent communication
- Modular design = easily expandable to new domains (mental health, women's wellness, etc.)

---

## 📊 Medical Report Generation Pipeline

The report generation process follows a **7-step pipeline**:

1. **Timeline Builder** – Organizes health data chronologically
2. **Trend Analyzer** – Detects changes in parameters over time
3. **Risk Scorer** – Computes personalized health risk indices
4. **Disease Inference** – Suggests possible conditions based on symptoms and labs
5. **Medication Aggregator** – Tracks prescription adherence & interactions
6. **Patient Report Generator** – Converts data into clear, patient-friendly summaries
7. **Report Aggregator** – Creates comprehensive dossiers for doctors or insurers

**Result**: A doctor-ready health story providing full context before consultation.

---

## 🧬 Gemini Live Integration

### Real-Time Conversational Intelligence
- **Gemini Live API** + **WebSockets** for instant dialogue
- Multilingual support with low latency
- Contextual memory keeps conversation history relevant
- Emotional Intelligence: conversational and compassionate tone
- Feels like a human companion, not a clinical bot

### Features
- Real-time audio streaming (bidirectional)
- Natural interruptions and turn-taking
- Voice synthesis with multiple voice options
- Tool calling capabilities for medical knowledge search and history access 

---

## 🌍 Alignment with Healthcare Vision

| Challenge | PraanLink Solution |
|-----------|-------------------|
| Lack of accessible care | Multilingual, low-bandwidth, continuous monitoring |
| Scattered health data | Multi-agent insight engine converting PDFs into readable insights |
| Explainable AI | Consent-centric, clinician-audited summaries |
| Inefficient workflows | Automated coordination + insurance guidance |

**Empathy + Engineering = Prevention for All**

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** (for backend and AI pipeline)
- **Node.js 18+** (for frontend)
- **PostgreSQL** (for database)
- **Google Cloud Account** (for Gemini Live API and ADK)
- **npm** or **bun** (for frontend dependencies)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PraanLink
   ```

2. **Backend Setup**
   ```bash
   cd PraanLink/backend
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp env.example .env
   # Edit .env with your DATABASE_URL and API keys
   
   # Initialize database (if needed)
   # The database will be initialized automatically on first run
   ```

3. **Frontend Setup**
   ```bash
   cd PraanLink/frontend
   
   # Install dependencies
   npm install
   # or
   bun install
   
   # Configure environment (if needed)
   # Create .env file with VITE_API_URL=http://localhost:8000
   ```

4. **AI Pipeline Setup**
   ```bash
   cd PraanLink/ai-pipeline
   
   # Activate the ADK virtual environment
   source adk-venv/bin/activate  # On Windows: adk-venv\Scripts\activate
   
   # Install dependencies (if not already installed)
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Backend** (Terminal 1)
   ```bash
   cd PraanLink/backend
   python main.py
   ```
   Backend runs on `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

2. **Start the Frontend** (Terminal 2)
   ```bash
   cd PraanLink/frontend
   npm run dev
   # or
   bun dev
   ```
   Frontend runs on `http://localhost:5173` (or port shown in terminal)

3. **Start the AI Pipeline** (Terminal 3)
   ```bash
   cd PraanLink/ai-pipeline
   source adk-venv/bin/activate
   adk api_server --allow_origins=http://localhost:8000 --host=0.0.0.0 --port=5010
   ```
   AI Pipeline runs on `http://localhost:5010`

### Environment Configuration

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/praanlink
GOOGLE_API_KEY=your_google_api_key
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_GEMINI_API_KEY=your_gemini_api_key
```

---

## 📁 Project Structure

```
PraanLink/
├── frontend/                 # React + TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   │   ├── CheckIn.tsx      # Weekly health check-ins
│   │   │   ├── Upload.tsx      # Document upload (lab reports, prescriptions)
│   │   │   ├── Summaries.tsx   # Health report summaries
│   │   │   ├── Appointments.tsx # Doctor appointment management
│   │   │   ├── AgentCall.tsx    # AI agent calling hospital
│   │   │   └── Insurance.tsx    # Insurance consultation
│   │   ├── utils/          # Utility functions
│   │   │   ├── gemini-live-api.js  # Gemini Live API wrapper
│   │   │   ├── audio-recorder.js   # Audio recording utilities
│   │   │   └── audio-streamer.js   # Audio playback utilities
│   │   └── App.tsx         # Main app component
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                 # FastAPI backend
│   ├── db/
│   │   ├── database.py     # Database connection
│   │   └── models.py       # SQLAlchemy models
│   ├── routers/            # API route handlers
│   │   ├── checkins.py     # Check-in endpoints
│   │   ├── prescriptions.py # Prescription endpoints
│   │   ├── reports.py      # Report endpoints
│   │   ├── hospitals.py    # Hospital endpoints
│   │   ├── insurances.py   # Insurance endpoints
│   │   └── appointments.py # Appointment endpoints
│   ├── utils/              # Utility functions
│   │   ├── transcribe.py   # Audio transcription
│   │   ├── summarize.py    # Conversation summarization
│   │   ├── ocr_summary.py  # OCR and document processing
│   │   ├── overall_report.py # Report generation
│   │   └── gmail_integration.py # Gmail API integration
│   ├── uploads/            # Uploaded files storage
│   ├── main.py            # FastAPI application
│   └── requirements.txt
│
└── ai-pipeline/            # Google ADK multi-agent system
    ├── conversation_summarizer_agent/  # Conversation processing
    ├── lab_report_agent/               # Lab report analysis
    │   └── subagents/                  # Lab report sub-agents
    ├── prescription_agent/              # Prescription analysis
    ├── report_agent/                   # Comprehensive report generation
    │   └── subagents/                  # Report generation sub-agents
    │       ├── TimelineBuilder/        # Step 1: Timeline construction
    │       ├── ClinicalTrendAnalyser/  # Step 2: Trend analysis
    │       ├── RiskScoringandSeverity/ # Step 3: Risk scoring
    │       ├── DiseaseInference/       # Step 4: Disease inference
    │       ├── MedicationAggregator/   # Step 5: Medication tracking
    │       ├── PatientReportGenerator/ # Step 6: Report generation
    │       └── ReportAggregator/       # Step 7: Final aggregation
    ├── adk-venv/           # ADK virtual environment
    └── requirements.txt
```

---

## 🔌 API Endpoints

### Check-ins
- `POST /upload-checkin` - Upload check-in audio recording
- `GET /api/checkins` - Get all check-ins
- `GET /api/checkins/{id}` - Get check-in by ID

### Prescriptions
- `POST /upload-prescription` - Upload prescription image
- `GET /api/prescriptions` - Get all prescriptions
- `GET /api/prescriptions/{id}` - Get prescription by ID

### Lab Reports
- `POST /upload-lab-report` - Upload lab report image
- `GET /api/reports` - Get all lab reports
- `GET /api/reports/{id}` - Get lab report by ID

### Overall Reports
- `POST /generate-overall-report` - Generate comprehensive health report
- `GET /latest-overall-report` - Get most recent overall report

### Insurance
- `POST /upload-insurance-consultation` - Upload insurance consultation audio
- `GET /api/insurances` - Get all insurance plans
- `GET /api/insurances/{id}` - Get insurance plan by ID

### Hospitals
- `GET /api/hospitals` - Get all hospitals
- `GET /api/hospitals/{id}` - Get hospital by ID
- `POST /api/hospitals` - Create hospital entry

### Appointments
- `GET /api/appointments` - Get all appointments
- `POST /api/appointments` - Create appointment

### File Serving
- `GET /uploads/{file_path}` - Serve uploaded files (PDFs, images, audio)

---

## 🎯 Features

### 1. Weekly Health Check-ins
- Natural, conversational check-ins via Gemini Live API
- Multilingual support (English, Hindi)
- Symptom tracking and mood monitoring
- AI-powered insights and recommendations

### 2. Document Processing
- **Lab Reports**: OCR extraction, abnormal parameter detection, risk scoring
- **Prescriptions**: Medication extraction, adherence tracking, interaction warnings

### 3. Comprehensive Health Reports
- Chronological timeline of all health events
- Trend analysis across lab reports
- Risk scoring and severity assessment
- Disease inference and medication overview
- Patient-friendly summaries and doctor-ready reports

### 4. Doctor Appointments
- AI agent that calls hospitals to book appointments
- Automatic email summaries sent to doctors
- Full medical context provided before consultation

### 5. Insurance Guidance
- Personalized insurance plan recommendations
- RAG-based matching using health profile
- Natural language consultation via Gemini Live

---

## 🔐 Security & Privacy

- All health data is stored securely in PostgreSQL
- File uploads are stored locally (can be configured for cloud storage)
- API keys should be kept in environment variables (never commit to git)
- CORS configured for development (should be restricted in production)
- User consent and data privacy should be implemented before production use

---

## 🧪 Testing

### Backend Testing
```bash
cd PraanLink/backend
python -m pytest  # If tests are implemented
```

### Frontend Testing
```bash
cd PraanLink/frontend
npm test  # If tests are implemented
```

---

## 🚧 Future Roadmap

### Phase 1: Core Enhancements
- [ ] User authentication and authorization
- [ ] Multi-user support with role-based access
- [ ] Enhanced data privacy and consent management

### Phase 2: IoT Integration
- [ ] Real-time data from wearables (Fitbit, Apple Watch)
- [ ] Blood pressure monitors and glucose monitors
- [ ] Automated data ingestion and trend detection

### Phase 3: Specialized Agents
- [ ] Mental health monitoring agent
- [ ] Nutrition and diet planning agent
- [ ] Women's wellness specialized agent

### Phase 4: Predictive Analytics
- [ ] Early detection of disease patterns
- [ ] Predictive risk modeling
- [ ] Personalized preventive recommendations

### Phase 5: Ecosystem Integration
- [ ] EHR (Electronic Health Record) API integration
- [ ] Insurance company API integration
- [ ] Hospital system integration
- [ ] End-to-end insurance management (application & tracking)

### Phase 6: Advanced Features
- [ ] Telemedicine integration
- [ ] Pharmacy integration for medication delivery
- [ ] Family health tracking
- [ ] Community health insights

---

## 📝 Development Guidelines

### Code Style
- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: Use ESLint and Prettier (configured in project)
- **TypeScript**: Strict type checking enabled

### Git Workflow
- Use feature branches for new features
- Write descriptive commit messages
- Keep commits atomic and focused

### Documentation
- Document API endpoints with FastAPI's automatic docs
- Add JSDoc comments for complex frontend functions
- Update README when adding major features

---

## 🐛 Troubleshooting

### Backend Issues
- **Database connection errors**: Check `DATABASE_URL` in `.env`
- **Port already in use**: Change port in `main.py` or kill existing process
- **Import errors**: Ensure virtual environment is activated

### Frontend Issues
- **API connection errors**: Verify `VITE_API_URL` points to running backend
- **Gemini API errors**: Check API key is valid and has quota
- **Build errors**: Clear `node_modules` and reinstall dependencies

### AI Pipeline Issues
- **ADK errors**: Ensure ADK virtual environment is activated
- **Agent errors**: Check agent configuration and API connections
- **Port conflicts**: Change port in `adk api_server` command

---

## 📄 License

[Specify your license here]

---

## 👥 Contributing

[Add contribution guidelines if open source]

---

## 📧 Contact

[Add contact information]

---

## 🙏 Acknowledgments

- Google Gemini Live API for real-time conversational AI
- Google ADK for multi-agent orchestration
- WhisperX for audio transcription
- FastAPI community
- React and TypeScript communities

---

**PraanLink** — Bringing continuous preventive healthcare to everyone, not just those with access to expensive systems.
