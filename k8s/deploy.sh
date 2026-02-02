#!/bin/bash

echo "====================================="
echo "Deploying ML API to Kubernetes"
echo "====================================="

# Build Docker image
echo "Building Docker image..."
docker build -t ml-api:v1 .

# Load image into Kubernetes (for Docker Desktop/Minikube)
if command -v minikube &> /dev/null; then
    echo "Loading image into Minikube..."
    minikube image load ml-api:v1
fi

# Create namespace
echo "Creating namespace..."
kubectl apply -f k8s/base/namespace.yaml

# Apply ConfigMap
echo "Applying ConfigMap..."
kubectl apply -f k8s/base/configmap.yaml

# Deploy application
echo "Deploying application..."
kubectl apply -f k8s/base/deployment.yaml

# Create service
echo "Creating service..."
kubectl apply -f k8s/base/service.yaml

# Apply HPA
echo "Applying Horizontal Pod Autoscaler..."
kubectl apply -f k8s/base/hpa.yaml

# Wait for deployment
echo "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/ml-api-deployment -n ml-system

# Get deployment status
echo ""
echo "====================================="
echo "Deployment Status"
echo "====================================="
kubectl get all -n ml-system

echo ""
echo "====================================="
echo "✅ Deployment Complete!"
echo "====================================="
echo ""
echo "Access the API:"
echo "  kubectl port-forward -n ml-system svc/ml-api-service 8080:80"
echo "  Then visit: http://localhost:8080"
echo ""
echo "View logs:"
echo "  kubectl logs -f -n ml-system deployment/ml-api-deployment"
echo ""
echo "Scale deployment:"
echo "  kubectl scale deployment ml-api-deployment -n ml-system --replicas=5"