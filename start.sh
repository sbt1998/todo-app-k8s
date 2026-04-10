#!/bin/bash
set -e

echo "╔══════════════════════════════════════════╗"
echo "║       Todo App — arranque en K8s         ║"
echo "╚══════════════════════════════════════════╝"

echo ""
echo "▶ [1/4] Verificando kubectl..."
if ! command -v kubectl &>/dev/null; then
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x kubectl && sudo mv kubectl /usr/local/bin/kubectl
  echo "    kubectl instalado."
else
  echo "    kubectl ya está instalado."
fi

echo ""
echo "▶ [2/4] Verificando minikube..."
if ! command -v minikube &>/dev/null; then
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  chmod +x minikube-linux-amd64 && sudo mv minikube-linux-amd64 /usr/local/bin/minikube
  echo "    minikube instalado."
else
  echo "    minikube ya está instalado."
fi

echo ""
echo "▶ [3/4] Arrancando clúster Kubernetes..."
if minikube status &>/dev/null; then
  echo "    El clúster ya está corriendo."
else
  minikube start --driver=docker --cpus=2 --memory=2048
fi

echo ""
echo "▶ [4/4] Construyendo imagen y desplegando..."
eval $(minikube docker-env)
docker build -t todo-app:latest ./app/
minikube addons enable metrics-server
kubectl apply -f ./k8s/

echo ""
echo "⏳ Esperando pods de app y db (máx 120s)..."
kubectl rollout status deployment/app --timeout=120s
kubectl rollout status deployment/db --timeout=120s

echo ""
kubectl get pods
kubectl get hpa

echo ""
echo "✅ ¡Todo listo! La app está corriendo en Kubernetes."
echo "   Para ver el escalado en tiempo real ejecuta:"
echo "   watch -n 5 kubectl get hpa"
