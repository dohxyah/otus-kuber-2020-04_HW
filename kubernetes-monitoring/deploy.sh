#!/bin/sh

kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f service-monitor.yaml

kubectl wait --for=condition=Available deployment/nginx-with-metrics --timeout=300s

kubectl get pods -o wide
kubectl get svc -o wide
kubectl get servicemonitors -o wide
