[![Build Status](https://travis-ci.com/otus-kuber-2020-04/dimpon_platform.svg?branch=master)](https://travis-ci.com/otus-kuber-2020-04/dimpon_platform)
# ДЗ по курсу "Инфраструктурная платформа на основе Kubernetes"
dimpon Platform repository




# Выполнено ДЗ №5

 - [ ] Основное ДЗ: Создать StatefulSet c - локальным S3 хранилищем
 - [ ] Задание со *: Повторить то же самое, но положить логин/пароль в Secret

## В процессе сделано:
 - StatefulSet развернут
 - StatefulSet развернут с логин/пароль в Secret

## Как запустить проект:
 - запустить manifests
    - miniostatefulset.yaml
    - minio-headlessservice.yaml
 - запустить для *
    - secrets.yaml
    - miniostatefulset-secured.yaml

## Как проверить работоспособность:
подключиться к ноде Kind, 10.244.3.5:9000 - Endpoint
```textmate
root@kind-worker2:/# curl http://10.244.3.6:9000
<?xml version="1.0" encoding="UTF-8"?>
<Error><Code>AccessDenied</Code><Message>Access Denied.</Message><Resource>/</Resource><RequestId>1617A54AAE7FAC81</RequestId><HostId>6ca6aa5c-906b-48e7-8eaa-e343f83715ac</HostId></Error>root@kind-worker2:/#


mc config host add mssminio http://10.244.3.5:9000 minio minio123

root@kind-worker2:/usr/mc# ./mc mb bucket ssminio
Bucket created successfully `bucket`.
Bucket created successfully `ssminio`.

root@kind-worker2:/usr/mc# ./mc stat ssminio
Name      : ssminio/
Date      : 2020-06-12 00:14:05 UTC
Size      : 4.0 KiB
Type      : folder
Metadata  :
  Content-Type       : application/octet-stream
  X-Amz-Meta-Mc-Attrs: atime:1591920848/ctime:1591920845/gid:0/gname:root/mode:16877/mtime:1591920845/uid:0/uname:root

```
Secrets:
```textmate
echo -n 'minio' | base64
bWluaW8=

echo -n 'minio123' | base64
bWluaW8xMjM=

# пересоздать StatefulSet

$ kubectl logs pod/minio-0
Endpoint:  http://10.244.3.6:9000  http://127.0.0.1:9000

Browser Access:
   http://10.244.3.6:9000  http://127.0.0.1:9000

Object API (Amazon S3 compatible):
   Go:         https://docs.min.io/docs/golang-client-quickstart-guide
   Java:       https://docs.min.io/docs/java-client-quickstart-guide
   Python:     https://docs.min.io/docs/python-client-quickstart-guide
   JavaScript: https://docs.min.io/docs/javascript-client-quickstart-guide
   .NET:       https://docs.min.io/docs/dotnet-client-quickstart-guide

#подключиться к minio

root@kind-worker2:/usr/mc# ./mc mb xxx  ssminio
Bucket created successfully `xxx`.
Bucket created successfully `ssminio`.
root@kind-worker2:/usr/mc# ./mc mb ls  ssminio
Bucket created successfully `ls`.
Bucket created successfully `ssminio`.

#проверить логин/пароль в контейнере minio

dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform/kubernetes-volumes (kubernetes-volumes)
$ kubectl exec -it minio-0 -- sh
/ #
/ # echo $MINIO_ACCESS_KEY
minio
/ # echo $MINIO_SECRET_KEY
minio123
/ #

```

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания

# Выполнено ДЗ № 4

 - [ ] Основное ДЗ сравнение iptables и IPVS, усановка MetalLB, развертывание Services(ClusterIP,LoadBalancer,Headless), Ingress
 - [ ] Задание со * Настроить service для внутреннего dns сервера

## В процессе сделано:
 - создал Deployment c 3 replicas, (maxSurge=0 maxUnavailable=0 запуски невозможен) поигрались с readinessProbe, livenessProbe (при livenessProbe.exec ксли проблемы,команда должна возвращать зачение отличное от 0) 
 - создал Service с ClusterIP
 - включил IPVS
 - поставил MetalLB
 - создал Service c LoadBalancer, сделал *
 - создал Headless Service, Ingress, сделал *

## Как запустить проект:
 - применить все манифесты. 
 - minikube ip  > ip route add 172.17.255.0/24 via <minikube ip>
 - dashboard kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.1/aio/deploy/recommended.yaml
 

## Как проверить работоспособность:
 - open http://172.17.255.1/index.html
 - open http://172.17.255.2/web/index.html
 - для * nslookup dns-udp-svc.kube-system.svc.cluster.local  172.17.255.10
 - nslookup web-svc-cip.default.svc.cluster.local  172.17.255.10
 - для * open dashboard https://172.17.255.2/dashboard/#/overview?namespace=default
 - для * curl -v -H "canary-header: true" http://someserver.com/    curl -v  http://someserver.com/

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания

# Выполнено ДЗ № 3

 - [ ] Основное ДЗ. Coздать ServiceAccounts, в рамках namespace, назначить различные роли


## В процессе сделано:
 - Пункт 1
 * Создать Service Account bob, дать ему роль admin в рамках всего
 кластера
 * Создать Service Account dave без доступа к кластеру
 - Пункт 2
 * Создать Namespace prometheus
 * Создать Service Account carol в этом Namespace
 * Дать всем Service Account в Namespace prometheus возможность
 делать get, list, watch в отношении Pods всего кластера
 - Пункт 3
 * Создать Namespace dev
 * Создать Service Account jane в Namespace dev
 * Дать jane роль admin в рамках Namespace dev
 * Создать Service Account ken в Namespace dev
 * Дать ken роль view в рамках Namespace dev


## Как запустить проект:
 - kubectl apply -f ....
:

## Как проверить работоспособность:
 - kubectl get serviceaccounts -n dev
 - kubectl get clusterroles -n dev | grep -v system:
 - kubectl get clusterrolebindings -n dev | grep -v system

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания
 
 
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
