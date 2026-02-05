# ⚡ Revolutionary Todo App

Welcome to the **Revolutionary Todo System**—a high-performance, futuristic todo management platform featuring an integrated AI Chatbot, multi-pane intelligence interface, and a production-grade Kubernetes deployment. Built with **Next.js**, **FastAPI**, and **Kubernetes**.

---

## 🚀 Quick Start (The Easiest Way)

If you have **Docker Desktop** installed on Windows, follow these 4 steps to see the magic:

1. **Spin up your Cluster**:
   ```powershell
   .\minikube start --cpus=4 --memory=6144
   .\minikube addons enable ingress
   .\minikube addons enable metrics-server
   ```

2. **Sync the Registry**:
   ```powershell
   .\minikube docker-env --shell powershell | Invoke-Expression
   ```

3. **Deploy Everything**:
   ```powershell
   # Build images inside Minikube
   docker build -t todo-backend:latest -f infra/docker/backend/Dockerfile .
   docker build -t todo-frontend:latest -f infra/docker/frontend/Dockerfile .

   # Launch the system
   .\helm install todo-chatbot infra/helm/todo-chatbot/
   ```

4. **Access the System**:
   ```powershell
   .\minikube service todo-chatbot-frontend --url
   ```

---

## 📂 System Architecture

- **Frontend**: Next.js 15+ (TypeScript, Tailwind, Framer Motion)
- **Backend**: FastAPI (Python 3.13, SQLModel ORM)
- **Intelligence**: Integrated OpenAI-powered todo chatbot
- **Infrastructure**: Docker Multi-stage builds & Helm v3 charts
- **Deployment**: Local Kubernetes (Minikube) with HPA (Auto-scaling)

---

## 🛠️ Component Setup

### 1. Prerequisites (For Windows)
- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/) (Enable WSL2)
- **Included Tools**: `minikube.exe` and `helm.exe` are already in the project root!
- **Kubectl**: Usually comes bundled with Docker Desktop.

### 2. Environment Configuration
The system uses a centralized **Helm ConfigMap** for Kubernetes deployments. For standard local dev, update `infra/helm/todo-chatbot/values.yaml`:

- `openai.apiKey`: Set your API key for the Chatbot feature.
- `database.url`: Default is set to a SQLite fallback, but supports Neon/PostgreSQL.

---

## 🧑‍💻 Manual Development

If you prefer to run services manually for rapid testing:

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔍 Health & Operations

Once deployed on Kubernetes, use these commands to monitor your system:

- **Check Pods**: `kubectl get pods`
- **View Scaling**: `kubectl get hpa` (Watches as backend scales up to 5 replicas)
- **System Logs**: `kubectl logs -l app=backend --tail=20`
- **Health Check**: Access `http://127.0.0.1:YOUR_PORT/health`

todo-app/
├── backend/              # FastAPI High-Performance API
├── frontend/             # Next.js 15+ Futuristic UI
├── infra/
│   ├── docker/           # Optimized Multi-stage Dockerfiles
│   └── helm/             # Orchestration & Auto-scaling logic
├── specs/                # Feature & Architecture Specifications
├── minikube.exe          # Portable Minikube binary

---

## ⚠️ Troubleshooting

- **Memory Error**: If Minikube fails to start, ensure Docker Desktop has at least 8GB of memory allocated in its Settings.
- **Port 3000 Busy**: If the frontend won't start, check if another node process is running.
- **Unauthorized**: Ensure you run `.\minikube start` BEFORE `.\helm install`.
- **Prefixes**: Always use `.\` before `minikube` or `helm` if you are using the binaries provided in the root folder.

---

*Built with ❤️ for the Revolutionary Developer.*