[![Build Status](https://travis-ci.com/otus-kuber-2020-04/dimpon_platform.svg?branch=master)](https://travis-ci.com/otus-kuber-2020-04/dimpon_platform)
# ДЗ по курсу "Инфраструктурная платформа на основе Kubernetes"
dimpon Platform repository

# Выполнено ДЗ № 1

 - [ ] Основное ДЗ
 * почему все pod в namespace kube-system
   восстановились после удаления. Укажите причину в описании PR.
   Pod-ы восстановил kubelet. Некоторые Pod-ы (Kube-dns) были восстановлены из ReplicaSet и видимо Scheduler вызвал kubelet.
   Другие pod-ы (etcd, kube-apiserver) были восстановлены по сигналам нативных процессов (kube-apiserver, kube-controller) которые запущены на master node
   kube-proxy был восстановлен из DaemonSet. Возможно за это отвечают контроллеры. Информация получена 
   ```
   kubectl describe pod
   kubectl get pod
    ```
   
 * Создать Docker image с простым web-server. Создать на его основе pod. Модифицировать дескриптор pod добавив Init Container. Задемплоить все в кластер  
   
 - [ ] Задание со *
 * Создать pod микросервиса frontend, задеплоить в кластер, выяснить почему не запустился.

## В процессе сделано:
 - Установлен Minikube, проверена его способность восстанавливаться, установлен Dashboard, k9s. 
 - Собран Docker image, задеплоен в Docker hub, сделан web-pod.yaml, задеплоен в кластер с Init Container и без.
 - Собран Docker image микросервиса frontend, задеплоен в кластер. Pod в статусе Error. Используем:
    ```
    kubectl describe .. 
    kubectl get pod ..
    kubectl logs ..
    видно, что не хватает environment variables
    из frontend.yaml берем переменные. Проверяем топологию системы по картинке на главном README.md  
    - про какие сервисы должен знать fronend 
    ```

## Как запустить проект:
 - Запуск web-pod
    ```
    kubectl apply -f web-pod.yaml
    kubectl port-forward --address 0.0.0.0 pod/web 8000:8000
    ```
 - Запуск frontend
    ```
    kubectl apply -f frontend-pod-healthy.yaml
    kubectl get pods - state is Running
    ```

## Как проверить работоспособность:
 - Перейти по ссылке http://localhost:8000 - отображается страница с лого Express42

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания
