# Project Descriptions for Recruiters

Use these descriptions in job applications, LinkedIn, and GitHub READMEs.
Each version is tailored for different role types.

---

## A. PraxisMed — AI Receptionist & Clinic Workflow Platform

### Short version (for CV bullets, LinkedIn):
> Built a multi-tenant AI receptionist and clinic workflow platform (FastAPI, Next.js, PostgreSQL, Vapi, Docker) for private medical practices. Human-in-the-loop architecture, 5,000+ automated tests, staging/demo-safe design.

### Medium version (for cover letter / About sections):
> PraxisMed is an AI-powered receptionist and workflow system for private medical practices in Vienna. It handles call intake, callback queue management, and provides a staff review dashboard. Built with FastAPI, Next.js, PostgreSQL, Vapi voice AI, Docker Compose, Railway and Vercel. Features multi-tenant cookie auth, audit/safety boundaries, and 5,000+ automated contract tests. Human-in-the-loop: no auto-diagnosis, staff review required at every step.

### For AI Engineer / Software Engineer roles:
> End-to-end multi-tenant SaaS: FastAPI REST backend, Next.js frontend, PostgreSQL multi-tenant schema, Vapi voice AI integration, Docker Compose, Railway/Vercel CI/CD. 5,000+ automated contract tests. Cookie-based auth with session management. Audit trails and human-in-the-loop safety boundaries.

### For MLOps / AI safety roles:
> Designed human-in-the-loop clinic AI workflow: voice intake via Vapi, structured callback queue, mandatory staff review before any patient contact. No auto-diagnosis, no PHI in production. Staging/demo-safe architecture with audit boundaries and 5,000+ automated safety/contract tests.

### For startup / product-oriented roles:
> Founded and built PraxisMed — an AI receptionist SaaS targeting private medical practices in Vienna. End-to-end: market research (1,245-lead database with priority scoring), product architecture (FastAPI/Next.js/PostgreSQL), and responsible AI design (human-in-the-loop, no auto-diagnosis, staff review required).

### What it proves:
- Can build and ship full-stack AI applications end-to-end
- Understands production-grade architecture (auth, multi-tenancy, Docker, CI/CD)
- Can design responsible AI systems with clear safety boundaries
- 5,000+ tests shows engineering discipline
- Self-directed: built without a team

---

## B. Cloud Demand Forecasting & Anomaly Detection

### Short version:
> End-to-end MLOps pipeline on M5 demand data: feature engineering, model training, FastAPI /forecast and /anomalies endpoints, Streamlit dashboard, Docker Compose, MAD Z-score anomaly detection.

### Medium version:
> Built an end-to-end demand forecasting and anomaly detection system (MLOps MVP). Data: M5-style daily time series (Store × Category). Pipeline: preprocessing → lag/rolling-window feature engineering → model training → FastAPI endpoints → Streamlit dashboard → Docker Compose packaging. Anomaly detection uses robust MAD Z-score for residual-based outlier flagging.

### For ML Engineer roles:
> End-to-end ML pipeline: feature engineering on M5-style demand time series (lag features, rolling-window features), model training with scikit-learn, REST API deployment via FastAPI (/forecast, /anomalies), Streamlit dashboard, Docker Compose.

### For Data Scientist roles:
> Demand forecasting and anomaly detection on M5-style daily retail data. Feature engineering: lag features, rolling-window statistics. Anomaly detection: robust MAD Z-score on model residuals. FastAPI API + Streamlit dashboard for visualization.

### For MLOps roles:
> MLOps MVP: training pipeline → model artifact → FastAPI serving endpoints → Streamlit dashboard → Docker Compose. REST API with validated Pydantic schemas for /forecast and /anomalies. Containerized, reproducible, version-controlled.

### What it proves:
- Can build and deploy ML models (not just train them)
- Understands MLOps pipeline design
- Knows FastAPI, Docker, and REST API design
- Time-series feature engineering and anomaly detection

---

## C. Human Development Analysis & Visualization

### Short version:
> Analyzed UNDP Human Development Report data (190+ countries) using Python (Pandas, Plotly) and Power BI. Built interactive dashboards across HDI, GII, GNI, and gender inequality indicators.

### For Data Analyst roles:
> End-to-end data analytics project: UNDP Human Development Report dataset (190+ countries). Data cleaning and preprocessing with Pandas. Multivariate statistical analysis of HDI, gender inequality, and income indicators. Interactive dashboards with Plotly and Power BI for stakeholder communication.

### For BI Analyst roles:
> Built Power BI dashboards on UNDP Human Development data. Designed visualizations for HDI trends, gender inequality (GII), and GNI per capita across 190+ countries. Translated multivariate data into clear business-style insights.

### What it proves:
- Can work with real-world messy data end-to-end
- Power BI dashboard design
- Statistical analysis and insight communication
- Python data stack (Pandas, Plotly, Matplotlib)

---

## D. Recommender Systems

### Short version:
> Implemented collaborative filtering and hybrid recommender systems in Python. Evaluated with Precision, Recall, and F1-score.

### For ML Engineer / Personalization roles:
> Built collaborative filtering and hybrid recommender systems with Python. Implemented user-item matrix factorization and hybrid approaches. Evaluated recommendations using standard IR metrics: Precision, Recall, F1-score.

### What it proves:
- Understanding of recommendation algorithms
- Ability to implement ML from scratch
- Knows evaluation metrics beyond accuracy

---

## Notes for Ali

- **Always match the project to the job.** Use PraxisMed for AI/software/startup roles. Use Forecasting for ML/MLOps/data science roles. Use Human Development for analytics/BI roles.
- **Never overclaim.** PraxisMed is staging/demo-safe — do not claim it handles live patient data.
- **GitHub repos should match.** Make sure the repo names and descriptions on GitHub.com match these descriptions.
