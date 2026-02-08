# Quickstart: Deploy Todo Chatbot on Minikube

## Prerequisites

- Docker Desktop with Kubernetes enabled OR Minikube installed
- Helm 3.x
- kubectl
- Git

## Local Development Setup

### 1. Clone and Navigate to Repository
```bash
git clone [repository-url]
cd todo-app
```

### 2. Start Minikube Cluster
```bash
minikube start --cpus=4 --memory=8192 --disk-size=40g
```

### 3. Enable Required Minikube Addons
```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

### 4. Build Docker Images
```bash
# For Minikube, point Docker CLI to Minikube's container registry
eval $(minikube docker-env)

# Build backend image
cd backend
docker build -t todo-backend:latest .

# Build frontend image
cd ../frontend
docker build -t todo-frontend:latest .
```

### 5. Install Helm Chart
```bash
cd ../infra/helm
helm install todo-chatbot ./todo-chatbot --values values.yaml
```

### 6. Complete Kubernetes Deployment Instructions

#### Building Docker Images for Minikube:
```bash
# Ensure you're in the project root
cd C:\new 1\Linux\todo-app

# Point Docker CLI to Minikube's container registry
eval $(minikube docker-env)

# Build backend image with proper tagging for local registry
docker build -t todo-backend:latest -f infra/docker/backend/Dockerfile .

# Build frontend image with proper tagging for local registry
docker build -t todo-frontend:latest -f infra/docker/frontend/Dockerfile .
```

#### Installing and Managing the Helm Chart:
```bash
# Navigate to the Helm chart directory
cd infra/helm

# Install the chart with default values
helm install todo-chatbot todo-chatbot/

# To upgrade the chart after making changes
helm upgrade todo-chatbot todo-chatbot/

# To uninstall the chart
helm uninstall todo-chatbot
```

#### Verifying the Deployment:
```bash
# Check if pods are running
kubectl get pods

# Check services
kubectl get services

# Check deployment status
kubectl get deployments

# View logs for backend
kubectl logs -l app=backend

# View logs for frontend
kubectl logs -l app=frontend
```

#### Accessing the Application:
```bash
# Get the Minikube IP to access the application
minikube ip

# Or use the service URL directly
minikube service todo-chatbot-frontend --url
```

### 6. Access the Application
```bash
# Get the Minikube IP
minikube ip

# Or create a tunnel for local access (recommended for development)
minikube service todo-frontend-service --url
```

## Verification Steps

1. Check all pods are running:
   ```bash
   kubectl get pods
   ```

2. Verify services are available:
   ```bash
   kubectl get services
   ```

3. Check application logs:
   ```bash
   kubectl logs -l app=todo-backend
   kubectl logs -l app=todo-frontend
   ```

4. Access the application in your browser at the provided URL

## Scaling the Application
```bash
# Scale backend replicas
kubectl scale deployment todo-backend --replicas=3

# Scale frontend replicas
kubectl scale deployment todo-frontend --replicas=2
```

## Troubleshooting

### Common Issues

1. **Images not found**: Ensure you ran `eval $(minikube docker-env)` before building images
2. **Insufficient resources**: Increase Minikube resources with `minikube delete` and restart with higher CPU/RAM
3. **Ingress not working**: Check ingress controller status with `kubectl get pods -n ingress-nginx`

### Useful Commands

- View all resources: `kubectl get all`
- Check resource usage: `kubectl top nodes` and `kubectl top pods`
- Port forward for debugging: `kubectl port-forward svc/todo-frontend-service 3000:80`
- View deployment status: `kubectl rollout status deployment/todo-backend`

## Cleanup

To remove the deployment:
```bash
helm uninstall todo-chatbot
```

To stop and delete Minikube cluster:
```bash
minikube stop
minikube delete
```