#!/bin/bash

# ML API Kubernetes Management Script

case "$1" in
  deploy)
    echo "🚀 Deploying ML API..."
    ./k8s/deploy.sh
    ;;
  
  status)
    echo "📊 Checking deployment status..."
    kubectl get all -n ml-system
    echo ""
    kubectl get hpa -n ml-system
    ;;
  
  logs)
    echo "📝 Streaming logs..."
    kubectl logs -f -n ml-system deployment/ml-api-deployment
    ;;
  
  scale)
    if [ -z "$2" ]; then
      echo "Usage: ./manage.sh scale <replicas>"
      exit 1
    fi
    echo "📈 Scaling to $2 replicas..."
    kubectl scale deployment ml-api-deployment -n ml-system --replicas=$2
    ;;
  
  port-forward)
    echo "🌐 Port forwarding to localhost:8080..."
    kubectl port-forward -n ml-system svc/ml-api-service 8080:80
    ;;
  
  test)
    echo "🧪 Running tests..."
    python tests/load_test.py
    ;;
  
  delete)
    echo "🗑️  Deleting deployment..."
    kubectl delete namespace ml-system
    ;;
  
  restart)
    echo "🔄 Restarting pods..."
    kubectl rollout restart deployment/ml-api-deployment -n ml-system
    ;;
  
  watch)
    echo "👀 Watching pods..."
    kubectl get pods -n ml-system --watch
    ;;
  
  metrics)
    echo "📈 Checking metrics..."
    kubectl top pods -n ml-system
    kubectl top nodes
    ;;
  
  *)
    echo "ML API Kubernetes Manager"
    echo ""
    echo "Usage: ./manage.sh <command>"
    echo ""
    echo "Commands:"
    echo "  deploy          Deploy application to Kubernetes"
    echo "  status          Check deployment status"
    echo "  logs            Stream application logs"
    echo "  scale <n>       Scale deployment to n replicas"
    echo "  port-forward    Forward service to localhost:8080"
    echo "  test            Run load tests"
    echo "  delete          Delete all resources"
    echo "  restart         Restart all pods"
    echo "  watch           Watch pod status"
    echo "  metrics         Show resource usage"
    exit 1
    ;;
esac