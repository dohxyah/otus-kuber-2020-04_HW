[![Build Status](https://travis-ci.com/otus-kuber-2020-04/dimpon_platform.svg?branch=master)](https://travis-ci.com/otus-kuber-2020-04/dimpon_platform)
# ДЗ по курсу "Инфраструктурная платформа на основе Kubernetes"
dimpon Platform repository


# Выполнено ДЗ № 2

 - [ ] Основное ДЗ развертывание Pod с помощью ReplicaSet и Deployment
 - [ ] Задание со * организовать Blue/Green Deployment и Reverse Rolling Update Deployment. Развернуть DaemonSet с node-exporter

## В процессе сделано:
 - Развернут кластер с помощью Kind. Проведены эксперименты с ReplicaSet. ReplicaSet только следит за количесивом реплик, не обновляет Pod если обновился image,
 в отличие от Deployment.
 - выполнены задания со звездочкой

## Как запустить проект:
 - Blue/Green Deployment вариант №1
    * Создать Service и 2 Deployment, у одного Deployment label.version = blue (replicas=3), у другого green(replicas=0). у Service selector настроен на blue
    * У Green Deployment ставим новую версию image, replicas=3, запускаем apply.
    * Переключаем Service на Green Deployment
    * Применяем replicas=3 к Blue Deployment
 - Blue/Green Deployment вариант №2
    * Создаем Deployment с 
    ```yaml   
   rollingUpdate:
      maxSurge: 100%
      maxUnavailable: 0
   ```
    * в момент apply с новым image создается новый ReplicaSet, c новым image, подниматся pod-ы
    * Затем начинают гасится Pod-ы старой ReplicaSet
 - Reverse Rolling Update Deployment
     * Создаем Deployment с 
     ```yaml   
    rollingUpdate:
       maxSurge: 1
       maxUnavailable: 0
    ```
     * в момент apply с новым image создается новый ReplicaSet, c новым image, подниматся pod-ы. 
       Но каждый новый Pod будет подниматься только когда опустится 1 старый тк  maxSurge: 1
 - Node Exporter развернут на всех нодах:
 ```
node-exporter-8sn8g               2/2     Running   0          2m25s   172.18.0.2    kind-worker3         <none>           <none>
node-exporter-qqlld               2/2     Running   0          2m25s   172.18.0.3    kind-worker          <none>           <none>
node-exporter-smt96               2/2     Running   0          2m25s   172.18.0.4    kind-worker2         <none>           <none>
node-exporter-w8mqz               2/2     Running   0          2m25s   172.18.0.5    kind-control-plane   <none>           <none>
```
       
## Как проверить работоспособность:
 - Blue/Green Deployment: kubectl apply -f paymentservice-deployment-bg.yaml|  kubectl get rs -l app=paymentservice  -w
 - Reverse Rolling Update Deployment: kubectl apply -f paymentservice-deployment-reverse.yaml|  kubectl get rs -l app=paymentservice  -w
 - DaemonSet: kubectl apply -f node-exporter-daemonset.yaml  kubectl get pods -l app=node-exporter -o wide 


## PR checklist:
 - [ ] Выставлен label с темой домашнего задания

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
