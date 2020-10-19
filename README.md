[![Build Status](https://travis-ci.com/otus-kuber-2020-04/dimpon_platform.svg?branch=master)](https://travis-ci.com/otus-kuber-2020-04/dimpon_platform)
# ДЗ по курсу "Инфраструктурная платформа на основе Kubernetes"
dimpon Platform repository

# Выполнено ДЗ № 12

 - [ ] Установлен CSI драйвер, создан pvc, pod, сделан snapshot, восстановлен pvc-pv из snapshot

## В процессе сделано:
 - Установлен CSI драйвер1
 - создан pvc, pod
 - сделан snapshot, восстановлен pvc-pv из snapshot

## Как запустить проект:
 
### Скачиваем репозиторий с CSI драйвером:
``git clone https://github.com/kubernetes-csi/csi-driver-host-path.git`` 
 
### Устанавливаем VolumeSnapshot CRD и Snapshot controller. Применяем CRD:
```./kubernetes-storage/hw/snapshotter.sh ``

### Устанавливаем CSI драйвер:
``./csi-driver-host-path/deploy/util/deploy-hostpath.sh ./kubernetes-1.18``
output как написано тут:
https://github.com/kubernetes-csi/csi-driver-host-path/blob/master/docs/deploy-1.17-and-later.md

проверяем
```
$ kubectl get pods
NAME                         READY   STATUS    RESTARTS   AGE
csi-hostpath-attacher-0      1/1     Running   0          2m57s
csi-hostpath-provisioner-0   1/1     Running   0          2m42s
csi-hostpath-resizer-0       1/1     Running   0          2m37s
csi-hostpath-snapshotter-0   1/1     Running   0          2m33s
csi-hostpath-socat-0         1/1     Running   0          2m27s
csi-hostpathplugin-0         3/3     Running   0          2m46s
snapshot-controller-0        1/1     Running   0          36m
```
### Ставим приложение
```
kubectl apply -f pvc.yaml
kubectl apply -f sc.yaml
kubectl apply -f pod.yaml
```
проверим
```
$ kubectl get sc -o wide
NAME                 PROVISIONER             RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
csi-hostpath-sc      hostpath.csi.k8s.io     Delete          Immediate              true                   84s
standard (default)   rancher.io/local-path   Delete          WaitForFirstConsumer   false                  58m

$ kubectl get pvc -o wide
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      AGE    VOLUMEMODE
storage-pvc   Bound    pvc-0d24cfcd-79f6-491b-83e0-a9bd021d25dc   1Gi        RWO            csi-hostpath-sc   102s   Filesystem

$ kubectl get pv -o wide
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                 STORAGECLASS      REASON   AGE    VOLUMEMODE
pvc-0d24cfcd-79f6-491b-83e0-a9bd021d25dc   1Gi        RWO            Delete           Bound    default/storage-pvc   csi-hostpath-sc            118s   Filesystem

$ kubectl get volumeattachment
NAME                                                                   ATTACHER              PV                                         NODE           ATTACHED   AGE
csi-0fdc78411df9826094540be2bb0588ada261c8c1253cfc32f3f7da09a9067512   hostpath.csi.k8s.io   pvc-0d24cfcd-79f6-491b-83e0-a9bd021d25dc   kind-worker2   true       2m56s

```
pod:
```
$ kubectl describe pods/storage-pod
Name:         storage-pod
Namespace:    default
Priority:     0
Node:         kind-worker2/172.18.0.3
Start Time:   Sat, 17 Oct 2020 23:44:25 +0200
Labels:       <none>
Annotations:  Status:  Running
IP:           10.244.3.8
IPs:
  IP:  10.244.3.8
Containers:
  nginx:
    Container ID:   containerd://ca9d5cbf1259e38888404d358a6e63ffa15976ecce76fd6bf36bb1b9587379b8
    Image:          nginx
    Image ID:       docker.io/library/nginx@sha256:ed7f815851b5299f616220a63edac69a4cc200e7f536a56e421988da82e44ed8
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Sat, 17 Oct 2020 23:44:53 +0200
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /data from custom-csi-volume (rw)
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-k6cjs (ro)
Conditions:
  Type              Status
  Initialized       True
  Ready             True
  ContainersReady   True
  PodScheduled      True
Volumes:
  custom-csi-volume:
    Type:       PersistentVolumeClaim (a reference to a PersistentVolumeClaim in the same namespace)
    ClaimName:  storage-pvc
    ReadOnly:   false
  default-token-k6cjs:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-k6cjs
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  <none>
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
                 node.kubernetes.io/unreachable:NoExecute for 300s
Events:
  Type    Reason                  Age    From                     Message
  ----    ------                  ----   ----                     -------
  Normal  Scheduled               5m41s  default-scheduler        Successfully assigned default/storage-pod to kind-worker2
  Normal  SuccessfulAttachVolume  5m41s  attachdetach-controller  AttachVolume.Attach succeeded for volume "pvc-0d24cfcd-79f6-491b-83e0-a9bd021d25dc"
  Normal  Pulling                 5m33s  kubelet, kind-worker2    Pulling image "nginx"
  Normal  Pulled                  5m14s  kubelet, kind-worker2    Successfully pulled image "nginx"
  Normal  Created                 5m13s  kubelet, kind-worker2    Created container nginx
  Normal  Started                 5m13s  kubelet, kind-worker2    Started container nginx

```

### создадим файл внутри Pod
```
$ kubectl exec -ti storage-pod bash
kubectl exec [POD] [COMMAND] is DEPRECATED and will be removed in a future version. Use kubectl kubectl exec [POD] -- [COMMAND] instead.
root@storage-pod:/#
root@storage-pod:/# cd data/
root@storage-pod:/data#
root@storage-pod:/data# echo 'Hello World! test file' > index.html
root@storage-pod:/data# cat index.html
Hello World! test file
root@storage-pod:/data#
```

### Создаем shapshot
``kubectl apply -f snapshot.yaml``
проверяем
```
$ kubectl get volumesnapshot
NAME       AGE
snapshot   40s
```

```
$ kubectl describe volumesnapshot snapshot
Name:         snapshot
Namespace:    default
Labels:       <none>
Annotations:  API Version:  snapshot.storage.k8s.io/v1beta1
Kind:         VolumeSnapshot
Metadata:
  Creation Timestamp:  2020-10-17T21:56:24Z
  Finalizers:
    snapshot.storage.kubernetes.io/volumesnapshot-as-source-protection
    snapshot.storage.kubernetes.io/volumesnapshot-bound-protection
  Generation:  1
  Managed Fields:
    API Version:  snapshot.storage.k8s.io/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:status:
        f:creationTime:
        f:readyToUse:
        f:restoreSize:
    Manager:         snapshot-controller
    Operation:       Update
    Time:            2020-10-17T21:56:25Z
  Resource Version:  13307
  Self Link:         /apis/snapshot.storage.k8s.io/v1beta1/namespaces/default/volumesnapshots/snapshot
  UID:               0ec7a00f-e957-495e-a039-82f5568d437c
Spec:
  Source:
    Persistent Volume Claim Name:  storage-pvc
  Volume Snapshot Class Name:      csi-hostpath-snapclass
Status:
  Bound Volume Snapshot Content Name:  snapcontent-0ec7a00f-e957-495e-a039-82f5568d437c
  Creation Time:                       2020-10-17T21:56:24Z
  Ready To Use:                        true
  Restore Size:                        1Gi
Events:                                <none>

```

```
$ kubectl get volumesnapshotcontents.snapshot.storage.k8s.io
NAME                                               AGE
snapcontent-0ec7a00f-e957-495e-a039-82f5568d437c   3m15s
```

```
$ kubectl describe volumesnapshotcontents.snapshot.storage.k8s.io snapcontent-0ec7a00f-e957-495e-a039-82f5568d437c
Name:         snapcontent-0ec7a00f-e957-495e-a039-82f5568d437c
Namespace:
Labels:       <none>
Annotations:  <none>
API Version:  snapshot.storage.k8s.io/v1beta1
Kind:         VolumeSnapshotContent
Metadata:
  Creation Timestamp:  2020-10-17T21:56:24Z
  Finalizers:
    snapshot.storage.kubernetes.io/volumesnapshotcontent-bound-protection
  Generation:  1
  Managed Fields:
    API Version:  snapshot.storage.k8s.io/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:status:
        .:
        f:creationTime:
        f:readyToUse:
        f:restoreSize:
        f:snapshotHandle:
    Manager:      csi-snapshotter
    Operation:    Update
    Time:         2020-10-17T21:56:24Z
    API Version:  snapshot.storage.k8s.io/v1beta1
    Fields Type:  FieldsV1
    fieldsV1:
      f:metadata:
        f:finalizers:
          .:
          v:"snapshot.storage.kubernetes.io/volumesnapshotcontent-bound-protection":
    Manager:         snapshot-controller
    Operation:       Update
    Time:            2020-10-17T21:56:24Z
  Resource Version:  13305
  Self Link:         /apis/snapshot.storage.k8s.io/v1beta1/volumesnapshotcontents/snapcontent-0ec7a00f-e957-495e-a039-82f5568d437c
  UID:               9f5356c5-d667-46a2-ad4f-a12c339a7c3e
Spec:
  Deletion Policy:  Delete
  Driver:           hostpath.csi.k8s.io
  Source:
    Volume Handle:             eaf14bed-10c1-11eb-be56-2ef9328635df
  Volume Snapshot Class Name:  csi-hostpath-snapclass
  Volume Snapshot Ref:
    API Version:       snapshot.storage.k8s.io/v1beta1
    Kind:              VolumeSnapshot
    Name:              snapshot
    Namespace:         default
    Resource Version:  13295
    UID:               0ec7a00f-e957-495e-a039-82f5568d437c
Status:
  Creation Time:    1602971784696642200
  Ready To Use:     true
  Restore Size:     1073741824
  Snapshot Handle:  999f808f-10c3-11eb-be56-2ef9328635df
Events:             <none>

```
проверим на ноде
```
$ docker exec -ti kind-worker2 bash
root@kind-worker2:/# cd /var/lib/csi-hostpath-data/
root@kind-worker2:/var/lib/csi-hostpath-data# ll
total 16
drwxr-xr-x  3 root root 4096 Oct 17 21:56 ./
drwxr-xr-x 13 root root 4096 Oct 17 21:30 ../
-rw-r--r--  1 root root  155 Oct 17 21:56 999f808f-10c3-11eb-be56-2ef9328635df.snap
drwxr-xr-x  2 root root 4096 Oct 17 21:53 eaf14bed-10c1-11eb-be56-2ef9328635df/
```

### Удаляем pod,pvc,pv:
```
kubectl delete pod storage-pod
kubectl delete pvc storage-pvc
kubectl get pv
No resources found in default namespace.
kubectl get pvc
No resources found in default namespace.
```

### восстанавливаем
``kubectl apply -f restore.yaml``

проверим
```
$ kubectl get pvc
NAME          STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      AGE
storage-pvc   Bound    pvc-1e4919ad-e9ea-4046-b0f8-214afc506d2c   1Gi        RWO            csi-hostpath-sc   36s
```

проверим данные в pod
kubectl apply -f pod.yaml

```
$ kubectl exec storage-pod -- cat data/index.html
Hello World! test file
```
Magic! index.html в Pod-e!


## PR checklist:
 - [ ] Выставлен label с темой домашнего задания

# Выполнено ДЗ № 11

 - [ ] установить flux, настроить деплой приложения и обновление через git
 - [ ] установить flagger, istio. Настроить canary deploy

## В процессе сделано:
 - создан кластер
 - установлен flux
 - создан репозиторий приложения в git lab, настроен pipeline для сборки и push docker images
 - настроен автодеплой и обновление манифестов
 - установлен istio, добавлены sidecrs
 - установлен flagger, настрооен canary deploy. 
 - контроль через Grafana

## Как запустить проект:
 - см readme

## Как проверить работоспособность:
 - см readme

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания

# Выполнено ДЗ № 11
# GitOps

###Подготовка

Репозиторий с microservices-demo:
https://gitlab.com/dimpon/microservices-demo

создаем кастер как в лекции по Istio:
```
#!/bin/bash
gcloud container clusters create \
  --machine-type n1-standard-2 \
  --num-nodes 4 \
  --zone europe-west4-a \
  --cluster-version latest \
  standart-cluster-1
```
проверяем:
```
$ gcloud container clusters list
NAME                LOCATION        MASTER_VERSION  MASTER_IP      MACHINE_TYPE   NODE_VERSION   NUM_NODES  STATUS
standart-cluster-1  europe-west4-a  1.16.13-gke.1   34.91.188.142  n1-standard-2  1.16.13-gke.1  4          RUNNING
```
ставим Istio as addon:
```
gcloud beta container clusters update standart-cluster-1 --update-addons=Istio=ENABLED --istio-config=auth=MTLS_PERMISSIVE
```
проверяем:
```
$ kubectl get pods -n istio-system
NAME                                             READY   STATUS      RESTARTS   AGE
istio-citadel-545687f6d-dpx9p                    1/1     Running     0          5m37s
istio-galley-774d87fcf8-dmv6p                    1/1     Running     0          5m37s
istio-ingressgateway-5b76747cbf-44t4q            1/1     Running     0          5m37s
istio-pilot-696f9747d7-c7tvx                     2/2     Running     1          5m36s
istio-policy-6b4b79789d-hc6sv                    2/2     Running     3          5m35s
istio-security-post-install-1.4.10-gke.5-wft9m   0/1     Completed   0          5m32s
istio-sidecar-injector-6cd98c4887-j5wqv          1/1     Running     0          5m35s
istio-telemetry-546b9b67bf-zz2bj                 2/2     Running     3          5m34s
promsd-696bcc5b96-dnhq4                          2/2     Running     1          5m34s
```
собиоаем docker images, обязательно из той директории где Dockerfile, проверяем:
https://hub.docker.com/repository/docker/dimpon/frontend
###GitOps
Установим CRD, добавляющую в кластер новый ресурс - HelmRelease:

``kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/master/deploy/crds.yaml``

Добавим официальный репозиторий Flux

``helm repo add fluxcd https://charts.fluxcd.io``

Произведем установку Flux в кластер, в namespace flux
```
kubectl create namespace flux
helm upgrade --install flux fluxcd/flux -f flux.values.yaml --namespace flux
```

Установим Helm operator:
```
helm upgrade --install helm-operator fluxcd/helm-operator -f helm-operator.values.yaml --namespace flux
```

Установим fluxctl на локальную машину
``choco install fluxctl``

добавим в свой профиль GitLab публичный ssh-ключ, flux'a
```text
$ fluxctl identity --k8s-fwd-ns flux
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDDeiOVZ0nqRYyacaxXmKgNfeFD566LXTiEGoHLzJrtZokDom972W/9aYTaA8HRBYOxv0jtzcKd2hmM7JgrRD0EGFCJnXWxQUdParVIdqDvT3nEm3i9WXz/kx7PmTwYm+cUWZZEJUlF00U+Ghexd8VdzEHA4SDjXpDYnDcbe/RuBRHXRr/O8eyolRaA0I6qxM+NIteMOzFygI1/w8kG3sekSQtnnjxlS2bq9
c1nseErWwnM2iBN+yMGuskLp38GTcwacIho6oR6BRapaBdbHT68df0+4uCVZMurvQH7NDdVmUOXgYwVwr5F2AX6xh5KDSXW2JUHMUwk97mU5oN7amipwO2Rcttir3Xvnd4lfLlqCo2carJfRWHpkCtXK8yoxpjEBmZtdAnH7y8KLzD2s4i5hVMc4itL3C3bu7hl0NuJSpuDAbmPJZYl+kziNZFmMNqd+NlKJDJx3JGRgjYe1/08DRJbYGbsrjGQfteCL6ncsa
xXHnQSs5AzuX4JuhqqL6k= root@flux-86794b8dc7-st92q
```

запушим новый namespace microservices-demo - и вот он в кластере!
```
$ kubectl get ns
NAME                 STATUS   AGE
default              Active   5h50m
flux                 Active   30m
istio-system         Active   4h21m
kube-node-lease      Active   5h50m
kube-public          Active   5h50m
kube-system          Active   5h50m
microservices-demo   Active   69s
```
log
```text
ts=2020-08-16T16:22:56.046582281Z caller=sync.go:540 method=Sync cmd=apply args= count=1
ts=2020-08-16T16:22:56.622646543Z caller=sync.go:606 method=Sync cmd="kubectl apply -f -" took=575.996188ms err=null output="namespace/microservices-demo created"
ts=2020-08-16T16:22:56.624366314Z caller=daemon.go:701 component=daemon event="Sync: 811d7e6, <cluster>:namespace/microservices-demo" logupstream=false
```
```text
$ kubectl get helmrelease -n microservices-demo
NAME       RELEASE    PHASE       STATUS     MESSAGE                                                                       AGE
frontend   frontend   Succeeded   deployed   Release was successful for Helm release 'frontend' in 'microservices-demo'.   46m
```

```text
$ kubectl get all -n microservices-demo
NAME                            READY   STATUS    RESTARTS   AGE
pod/frontend-6b8b79c478-kvm4m   1/1     Running   0          66s

NAME               TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/frontend   ClusterIP   10.59.255.20   <none>        80/TCP    18m

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/frontend   1/1     1            1           18m

NAME                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/frontend-6b8b79c478   1         1         1       66s
replicaset.apps/frontend-7c7456c89    0         0         0       18m
```
обновим frontend image, сделаем push.
frontend deployment обновился, обновился также deploy/releases/frontend.yaml, линк на картинку
[frontendupdated.PNG](./kubernetes-gitops/frontendupdated.PNG)

переименуем deployment - frontend передеплоился
```
$  helm history frontend -n microservices-demo
REVISION        UPDATED                         STATUS          CHART           APP VERSION     DESCRIPTION
1               Mon Aug 17 22:03:41 2020        superseded      frontend-0.21.0 1.16.0          Install complete
2               Mon Aug 17 22:21:17 2020        superseded      frontend-0.21.0 1.16.0          Upgrade complete
3               Mon Aug 17 22:30:22 2020        deployed        frontend-0.21.0 1.16.0          Upgrade complete
```
helm-operator log:
```
ts=2020-08-17T22:30:22.700124895Z caller=helm.go:69 component=helm version=v3 info="Looks like there are no changes for Service \"frontend\"" targetNamespace=microservices-demo release=frontend
ts=2020-08-17T22:30:22.710500256Z caller=helm.go:69 component=helm version=v3 info="Created a new Deployment called \"frontend-hipster\" in microservices-demo\n" targetNamespace=microservices-demo release=frontend
ts=2020-08-17T22:30:22.720065545Z caller=helm.go:69 component=helm version=v3 info="Looks like there are no changes for Gateway \"frontend-gateway\"" targetNamespace=microservices-demo release=frontend
ts=2020-08-17T22:30:22.736562828Z caller=helm.go:69 component=helm version=v3 info="Looks like there are no changes for VirtualService \"frontend\"" targetNamespace=microservices-demo release=frontend
ts=2020-08-17T22:30:22.741143991Z caller=helm.go:69 component=helm version=v3 info="Deleting \"frontend\" in microservices-demo..." targetNamespace=microservices-demo release=frontend
```
Добаим манифесты HelmRelease для всех микросервисов входящих в состав HipsterShop.

При обновлении Images происхоит редеплой, при обновлении манифестов тоже. Класс!

###Canary deployments с Flagger и Istio
Istio уже установлен, скачиваем istioctl
Установка Flagger

Добавление helm-репозитория flagger:

```
helm repo add flagger https://flagger.app
```
Установка CRD для Flagger:
```
kubectl apply -f https://raw.githubusercontent.com/weaveworks/flagger/master/artifacts/flagger/crd.yaml
```
Установка flagger с указанием использовать Istio:
```
helm upgrade --install flagger flagger/flagger --namespace=istio-system --set crd.create=false \
 --set meshProvider=istio \
 --set metricsServer=http://prometheus:9090
```
Sidecar Injection
добавим ``istio-injection: enabled`` к namespace  microservices-demo
проверим:
```
$ kubectl get ns microservices-demo --show-labels
NAME                 STATUS   AGE     LABELS
microservices-demo   Active   5d23h   fluxcd.io/sync-gc-mark=sha256.E01-msAVm7rQfQ2CdkUMjIEdleNITa295iNRhKeMuxE,istio-injection=enabled
```

добавим sidecar удалив Pods
```
kubectl delete pods --all -n microservices-demo
```
После этого можно проверить, что контейнер с названием istioproxy появился внутри каждого pod:
```
kubectl describe pod -l app=frontend -n microservices-demo
```
VirtualService и Gateway уже были созданы, так как были в helm charts frontend
```
$ kubectl get gateway -n microservices-demo
NAME               AGE
frontend-gateway   4d17h
```
установим Canary добавив canary.yaml в deploy\charts\frontend\templates
благодяря Flux он задеплоится автоматически
```
$ kubectl get canary -n microservices-demo
NAME       STATUS        WEIGHT   LASTTRANSITIONTIME
frontend   Initialized   0        2020-08-23T14:16:00Z
```
frontend pod обновился:
```
$ kubectl get pods -n microservices-demo -l app=frontend-primary
NAME                                READY   STATUS    RESTARTS   AGE
frontend-primary-698b698db9-5j6fn   2/2     Running   0          3m47s
```
соберем v0.0.3 для frontend
```text
kubectl describe canary frontend -n microservices-demo

Events:
  Type     Reason  Age                From     Message
  ----     ------  ----               ----     -------
  Warning  Synced  18m                flagger  frontend-primary.microservices-demo not ready: waiting for rollout to finish: observed deployment generation less then desired generation
  Warning  Synced  17m (x2 over 18m)  flagger  Error checking metric providers: prometheus not avaiable: running query failed: request failed: Get "http://prometheus:9090/api/v1/query?query=vector%281%29": dial tcp: lookup prometheus on 10.59.240.10:53: no such host
  Normal   Synced  17m                flagger  Initialization done! frontend.microservices-demo
  Normal   Synced  3m37s              flagger  New revision detected! Scaling up frontend.microservices-demo
  Normal   Synced  2m37s              flagger  Starting canary analysis for frontend.microservices-demo
  Normal   Synced  2m37s              flagger  Advance frontend.microservices-demo canary weight 10
  Warning  Synced  97s                flagger  Prometheus query failed: running query failed: request failed: Get "http://prometheus:9090/api/v1/query?query=+sum%28+rate%28+istio_requests_total%7B+reporter%3D%22destination%22%2C+destination_workload_namespace%3D%22microservices-demo%22%2C+destination_workload%3D~%22frontend%22%2C+response_code%21~%225.%2A%22+%7D%5B1m%5D+%29+%29+%2F+sum%28+rate%28+istio_requests_total%7B+reporter%3D%22destination%22%2C+destination_workload_namespace%3D%22microservices-demo%22%2C+destination_workload%3D~%22frontend%22+%7D%5B1m%5D+%29+%29+%2A+100": dial tcp: lookup prometheus on 10.59.240.10:53: no such host
  Warning  Synced  37s                flagger  Rolling back frontend.microservices-demo failed checks threshold reached 1
  Warning  Synced  37s                flagger  Canary failed! Scaling down frontend.microservices-demo
```
ага, нет Prometheus:

надо ставить правильный Prometheus! и поправить манифест:
```
wget https://storage.googleapis.com/gke-release/istio/release/1.0.6-gke.1/patches/install-prometheus.yaml
kubectl -n istio-system apply -f install-prometheus.yaml
```
теперь проблема с request-success-rate метрикой, ее никто не поставляет.

поставим графану
```
helm upgrade -i flagger-grafana flagger/grafana \
--namespace=istio-system \
--set url=http://prometheus:9090 \
--set user=admin \
--set password=admin
```
пересобираем и пушим frontend image - работает!
[canary.PNG](./kubernetes-gitops/canary.PNG)
```text
$ kubectl get canaries -n microservices-demo
NAME       STATUS      WEIGHT   LASTTRANSITIONTIME
frontend   Succeeded   0        2020-08-24T08:01:27Z

```
```text
Events:
  Type     Reason  Age                From     Message
  ----     ------  ----               ----     -------
  Warning  Synced  43m                flagger  frontend-primary.microservices-demo not ready: waiting for rollout to finish: observed deployment generation less then desired generation
  Normal   Synced  43m (x2 over 43m)  flagger  all the metrics providers are available!
  Normal   Synced  43m                flagger  Initialization done! frontend.microservices-demo
  Normal   Synced  30m (x2 over 38m)  flagger  Starting canary analysis for frontend.microservices-demo
  Normal   Synced  20m (x3 over 38m)  flagger  New revision detected! Scaling up frontend.microservices-demo
  Normal   Synced  20m (x2 over 38m)  flagger  Advance frontend.microservices-demo canary weight 10
  Normal   Synced  20m (x4 over 35m)  flagger  (combined from similar events): Starting canary analysis for frontend.microservices-demo
  Normal   Synced  19m (x3 over 37m)  flagger  Advance frontend.microservices-demo canary weight 20
  Normal   Synced  19m (x3 over 37m)  flagger  Advance frontend.microservices-demo canary weight 30
  Normal   Synced  18m (x2 over 36m)  flagger  Copying frontend.microservices-demo template spec to frontend-primary.microservices-demo
  Normal   Synced  18m (x3 over 36m)  flagger  Routing all traffic to primary
  Normal   Synced  17m (x2 over 27m)  flagger  Promotion completed! Scaling down frontend.microservices-demo

$ kubectl get pods -n microservices-demo
NAME                                     READY   STATUS    RESTARTS   AGE
adservice-d9cccddc7-829np                2/2     Running   0          14h
cartservice-5777d679cb-x9948             2/2     Running   3          14h
cartservice-redis-master-0               2/2     Running   0          14h
checkoutservice-7b5c745c-7brg5           2/2     Running   0          14h
currencyservice-9cc946bc5-nllpw          2/2     Running   0          14h
emailservice-b8bc9bb75-q7z7v             2/2     Running   0          14h
frontend-79c5b4954b-4nd4s                2/2     Running   0          82s
frontend-primary-78dc4d7794-lg882        2/2     Running   0          9m22s
loadgenerator-75c8675578-ds9dz           2/2     Running   1          14h
paymentservice-cd9c5b799-tgns2           2/2     Running   0          14h
productcatalogservice-5b7469cd59-jtmxp   2/2     Running   0          14h
recommendationservice-6845f785f4-q7w48   2/2     Running   0          14h
shippingservice-66f9bf485d-mgnfl         2/2     Running   0          14h
```

# Выполнено ДЗ № 10
# Hashicorp Vault + k8s

устанавливаем прежде всего nginx-ingress
```
kubectl create ns nginx-ingress
helm upgrade --install nginx-ingress stable/nginx-ingress --wait --namespace=nginx-ingress --version=1.11.1
IP:34.90.132.76
```
устанавливаем Consul, Vault, проверяем статус
```
git clone https://github.com/hashicorp/consul-helm.git
# helm install consul ../consul-helm
helm upgrade --install consul-helm ../consul-helm

git clone https://github.com/hashicorp/vault-helm.git
helm upgrade --install vault ../vault-helm -f kubernetes-vault/vault.values.yaml
helm status vault

$ helm status vault
NAME: vault
LAST DEPLOYED: Fri Jul 31 21:59:57 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing HashiCorp Vault!

Now that you have deployed Vault, you should look over the docs on using
Vault with Kubernetes available here:

https://www.vaultproject.io/docs/


Your release is named vault. To learn more about the release, try:

  $ helm status vault
  $ helm get vault
```
pods:
```text
$ kubectl get pod -l app.kubernetes.io/instance=vault
NAME                                    READY   STATUS    RESTARTS   AGE
vault-0                                 0/1     Running   0          17m
vault-1                                 0/1     Running   0          17m
vault-2                                 0/1     Running   0          17m
vault-agent-injector-78865dd548-r54mx   1/1     Running   0          17m

$ kubectl logs vault-0 --tail=5
2020-07-31T20:18:08.347Z [INFO]  core: seal configuration missing, not initialized
2020-07-31T20:18:11.351Z [INFO]  core: seal configuration missing, not initialized
2020-07-31T20:18:14.349Z [INFO]  core: seal configuration missing, not initialized
2020-07-31T20:18:17.345Z [INFO]  core: seal configuration missing, not initialized
2020-07-31T20:18:20.360Z [INFO]  core: seal configuration missing, not initialized
```
Инициализируем Vault:
```
$ kubectl exec -it vault-0 -- vault operator init --key-shares=1 --key-threshold=1
Unseal Key 1: k7dLD+sdp1uZJewnW8KFy8CignbXWNsqBYKipb2Rerg=

Initial Root Token: s.wHTxv9lhN5QKQc3erpBQRsqq

Vault initialized with 1 key shares and a key threshold of 1. Please securely
distribute the key shares printed above. When the Vault is re-sealed,
restarted, or stopped, you must supply at least 1 of these keys to unseal it
before it can start servicing requests.

Vault does not store the generated master key. Without at least 1 key to
reconstruct the master key, Vault will remain permanently sealed!

It is possible to generate new unseal keys, provided you have a quorum of
existing unseal keys shares. See "vault operator rekey" for more information.
```
Pods are sealed:
```text
$ kubectl exec -it vault-0 -- vault status
Key                Value
---                -----
Seal Type          shamir
Initialized        true
Sealed             true
Total Shares       1
Threshold          1
Unseal Progress    0/1
Unseal Nonce       n/a
Version            1.4.2
HA Enabled         true
command terminated with exit code 2
```
Unseal:
```
dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform (kubernetes-vault)
$ kubectl exec -it vault-0 -- vault operator unseal
Unseal Key (will be hidden):
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.4.2
Cluster Name    vault-cluster-ec2b29fd
Cluster ID      9558dc93-09a6-026a-db90-fcad30a25d4c
HA Enabled      true
HA Cluster      https://vault-0.vault-internal:8201
HA Mode         active

dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform (kubernetes-vault)
$ kubectl exec -it vault-1 -- vault operator unseal
Unseal Key (will be hidden):
Key                    Value
---                    -----
Seal Type              shamir
Initialized            true
Sealed                 false
Total Shares           1
Threshold              1
Version                1.4.2
Cluster Name           vault-cluster-ec2b29fd
Cluster ID             9558dc93-09a6-026a-db90-fcad30a25d4c
HA Enabled             true
HA Cluster             https://vault-0.vault-internal:8201
HA Mode                standby
Active Node Address    http://10.0.0.11:8200

dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform (kubernetes-vault)
$ kubectl exec -it vault-2 -- vault operator unseal
Unseal Key (will be hidden):
Key                    Value
---                    -----
Seal Type              shamir
Initialized            true
Sealed                 false
Total Shares           1
Threshold              1
Version                1.4.2
Cluster Name           vault-cluster-ec2b29fd
Cluster ID             9558dc93-09a6-026a-db90-fcad30a25d4c
HA Enabled             true
HA Cluster             https://vault-0.vault-internal:8201
HA Mode                standby
Active Node Address    http://10.0.0.11:8200
```
Status:
```
dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform (kubernetes-vault)
$ kubectl exec -it vault-0 -- vault status
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.4.2
Cluster Name    vault-cluster-ec2b29fd
Cluster ID      9558dc93-09a6-026a-db90-fcad30a25d4c
HA Enabled      true
HA Cluster      https://vault-0.vault-internal:8201
HA Mode         active

dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform (kubernetes-vault)
$ kubectl exec -it vault-1 -- vault status
Key                    Value
---                    -----
Seal Type              shamir
Initialized            true
Sealed                 false
Total Shares           1
Threshold              1
Version                1.4.2
Cluster Name           vault-cluster-ec2b29fd
Cluster ID             9558dc93-09a6-026a-db90-fcad30a25d4c
HA Enabled             true
HA Cluster             https://vault-0.vault-internal:8201
HA Mode                standby
Active Node Address    http://10.0.0.11:8200

dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform (kubernetes-vault)
$ kubectl exec -it vault-2 -- vault status
Key                    Value
---                    -----
Seal Type              shamir
Initialized            true
Sealed                 false
Total Shares           1
Threshold              1
Version                1.4.2
Cluster Name           vault-cluster-ec2b29fd
Cluster ID             9558dc93-09a6-026a-db90-fcad30a25d4c
HA Enabled             true
HA Cluster             https://vault-0.vault-internal:8201
HA Mode                standby
Active Node Address    http://10.0.0.11:8200
```
Login to Vault:
```text
$ kubectl exec -it vault-0 -- vault login
Token (will be hidden):
Success! You are now authenticated. The token information displayed below
is already stored in the token helper. You do NOT need to run "vault login"
again. Future Vault requests will automatically use this token.

Key                  Value
---                  -----
token                s.wHTxv9lhN5QKQc3erpBQRsqq
token_accessor       O31la7yqc3nPjAlQgjW7hWOJ
token_duration       ∞
token_renewable      false
token_policies       ["root"]
identity_policies    []
policies             ["root"]
```
```
$ kubectl exec -it vault-0 -- vault auth list
Path      Type     Accessor               Description
----      ----     --------               -----------
token/    token    auth_token_b50339b0    token based credentials
```
Создадим secrets:
```text
kubectl exec -it vault-0 -- vault secrets enable --path=otus kv
kubectl exec -it vault-0 -- vault secrets list --detailed
kubectl exec -it vault-0 -- vault kv put otus/otus-ro/config username='otus' password='asajkjkahs'
kubectl exec -it vault-0 -- vault kv put otus/otus-rw/config username='otus' password='asajkjkahs'
kubectl exec -it vault-0 -- vault read otus/otus-ro/config
kubectl exec -it vault-0 -- vault kv get otus/otus-rw/config
```
И прочитаем их:
```text
$ kubectl exec -it vault-0 -- vault read otus/otus-ro/config
Key                 Value
---                 -----
refresh_interval    768h
password            asajkjkahs
username            otus

$ kubectl exec -it vault-0 -- vault kv get otus/otus-rw/config
====== Data ======
Key         Value
---         -----
password    asajkjkahs
username    otus
```
### Включим авторизацию черерз k8s
```text
kubectl exec -it vault-0 -- vault auth enable kubernetes
kubectl exec -it vault-0 -- vault auth list
```
обновленный список:
```
$ kubectl exec -it vault-0 -- vault auth list
Path           Type          Accessor                    Description
----           ----          --------                    -----------
kubernetes/    kubernetes    auth_kubernetes_c309310a    n/a
token/         token         auth_token_b50339b0         token based credentials
```
Создадим Service Account и Binding

```text
kubectl apply -f service-account.yml
kubectl apply -f vault-auth-service-account.yml
```
Подготовим переменные для записи в конфиг кубер авторизации
```text
export VAULT_SA_NAME=$(kubectl get sa vault-auth -o jsonpath="{.secrets[*]['name']}")
export SA_JWT_TOKEN=$(kubectl get secret $VAULT_SA_NAME -o jsonpath="{.data.token}" | base64 --decode; echo)
export SA_CA_CRT=$(kubectl get secret $VAULT_SA_NAME -o jsonpath="{.data['ca\.crt']}" | base64 --decode; echo)
export K8S_HOST=$(more ~/.kube/config | grep server | awk '/http/ {print $NF}')
```
Запишем конфиг в vault
```
kubectl exec -it vault-0 -- vault write auth/kubernetes/config token_reviewer_jwt="$SA_JWT_TOKEN" kubernetes_host="$K8S_HOST" kubernetes_ca_cert="$SA_CA_CRT"
```
создадим политку и роль в vault
```
kubectl cp otus-policy.hcl vault-0:./
kubectl exec -it vault-0 -- vault policy write otus-policy /otus-policy.hcl
kubectl exec -it vault-0 -- vault write auth/kubernetes/role/otus bound_service_account_names=vault-auth bound_service_account_namespaces=default policies=otus-policy ttl=24h
```
в принципе все это можно сделать через UI [policy.PNG](./kubernetes-vault/screenshots/policy.PNG)
[role.PNG](./kubernetes-vault/screenshots/role.PNG)
[binding.PNG](./kubernetes-vault/screenshots/binding.PNG)
Проверим как работает авторизация
```
kubectl run --generator=run-pod/v1 tmp --rm -i --tty --serviceaccount=vault-auth --image alpine:3.7
apk add curl jq

VAULT_ADDR=http://vault:8200
KUBE_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)

curl --request POST --data '{"jwt": "'$KUBE_TOKEN'", "role": "otus"}' $VAULT_ADDR/v1/auth/kubernetes/login | jq

TOKEN=$(curl -k -s --request POST --data '{"jwt": "'$KUBE_TOKEN'", "role": "test"}' $VAULT_ADDR/v1/auth/kubernetes/login | jq '.auth.client_token' | awk -F\" '{print $2}')

/ # VAULT_ADDR=http://vault:8200
/ # KUBE_TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
/ # curl --request POST --data '{"jwt": "'$KUBE_TOKEN'", "role": "otus"}' $VAULT_ADDR/v1/auth/kubernetes/login | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
{ 0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
  "request_id": "8fbfeb42-6b45-d1ad-d60d-fd88093d4f59",
  "lease_id": "",
  "renewable": false,
  "lease_duration": 0,
  "data": null,
  "wrap_info": null,
  "warnings": null,
  "auth": {
    "client_token": "s.DTb1bYFr81eXnw6Qhjd8YlNF",
    "accessor": "Ijo5tvK5wnUp6jFfIbfI903g",
    "policies": [
      "default",
      "otus-policy"
    ],
    "token_policies": [
      "default",
      "otus-policy"
    ],
    "metadata": {
      "role": "otus",
      "service_account_name": "vault-auth",
      "service_account_namespace": "default",
      "service_account_secret_name": "vault-auth-token-62zqj",
      "service_account_uid": "fccc6df2-6436-4bf5-a71c-e82e30a1cc13"
    },
    "lease_duration": 86400,
    "renewable": true,
    "entity_id": "099c0a42-ce20-74b9-3880-c943e2c53375",
    "token_type": "service",
    "orphan": true
  }
}
```
Прочитаем записанные ранее секреты и попробуем их обновить
```text
curl --header "X-Vault-Token:s.DTb1bYFr81eXnw6Qhjd8YlNF" $VAULT_ADDR/v1/otus/otus-ro/config
curl --header "X-Vault-Token:s.DTb1bYFr81eXnw6Qhjd8YlNF" $VAULT_ADDR/v1/otus/otus-rw/config

curl --request POST --data '{"bar": "baz"}' --header "X-Vault-Token:s.DTb1bYFr81eXnw6Qhjd8YlNF" $VAULT_ADDR/v1/otus/otus-ro/config | jq
curl --request POST --data '{"bar": "baz"}' --header "X-Vault-Token:s.DTb1bYFr81eXnw6Qhjd8YlNF" $VAULT_ADDR/v1/otus/otus-rw/config | jq
curl --request POST --data '{"bar": "baz"}' --header "X-Vault-Token:s.DTb1bYFr81eXnw6Qhjd8YlNF" $VAULT_ADDR/v1/otus/otus-rw/config1 | jq
```
у обоих полиси нет прав "update" но у  otus/otus-rw/  есть create
добавим update, see screen, повторим
curl --request POST --data '{"bar": "baz"}' --header "X-Vault-Token:s.DTb1bYFr81eXnw6Qhjd8YlNF" $VAULT_ADDR/v1/otus/otus-rw/config | jq
[add_update.PNG](./kubernetes-vault/screenshots/add_update.PNG)

## Use case использования авторизации через кубер
установим Pod c nginx + Init container c Vault-agent он будет передавать secrets в Pod 
```text
kubectl apply -f configs-k8s/example-k8s-configmap.yaml
kubectl apply -f configs-k8s/example-k8s-pods.yaml
kubectl apply -f configs-k8s/example-k8s-svc-ingress.yaml
```
Confid Map:
```text
$ kubectl get configmap example-vault-agent-config -o yaml
apiVersion: v1
data:
  vault-agent-config.hcl: |
    # Comment this out if running as sidecar instead of initContainer
    exit_after_auth = true

    pid_file = "/home/vault/pidfile"

    auto_auth {
        method "kubernetes" {
            mount_path = "auth/kubernetes"
            config = {
                role = "otus"
            }
        }

        sink "file" {
            config = {
                path = "/home/vault/.vault-token"
            }
        }
    }

    template {
    destination = "/etc/secrets/index.html"
    contents = <<EOT
    <html>
    <body>
    <p>Some secrets:</p>
    {{- with secret "otus/otus-ro/config" }}
    <ul>
    <li><pre>username: {{ .Data.username }}</pre></li>
    <li><pre>password: {{ .Data.password }}</pre></li>
    </ul>
    {{ end }}
    </body>
    </html>
    EOT
    }
kind: ConfigMap
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","data":{"vault-agent-config.hcl":"# Comment this out if running as sidecar instead of initContainer\nexit_after_auth = true\n\npid_file = \"/home/vault/pidfile\"\n\nauto_auth {\n    method \"kubernetes\" {\n        mount_path = \"auth/kuber
netes\"\n        config = {\n            role = \"otus\"\n        }\n    }\n\n    sink \"file\" {\n        config = {\n            path = \"/home/vault/.vault-token\"\n        }\n    }\n}\n\ntemplate {\ndestination = \"/etc/secrets/index.html\"\ncontents = \u003c\u
003cEOT\n\u003chtml\u003e\n\u003cbody\u003e\n\u003cp\u003eSome secrets:\u003c/p\u003e\n{{- with secret \"otus/otus-ro/config\" }}\n\u003cul\u003e\n\u003cli\u003e\u003cpre\u003eusername: {{ .Data.username }}\u003c/pre\u003e\u003c/li\u003e\n\u003cli\u003e\u003cpre\u0
03epassword: {{ .Data.password }}\u003c/pre\u003e\u003c/li\u003e\n\u003c/ul\u003e\n{{ end }}\n\u003c/body\u003e\n\u003c/html\u003e\nEOT\n}\n"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"example-vault-agent-config","namespace":"default"}}
  creationTimestamp: "2020-08-01T21:26:00Z"
  name: example-vault-agent-config
  namespace: default
  resourceVersion: "384927"
  selfLink: /api/v1/namespaces/default/configmaps/example-vault-agent-config
  uid: 0b8bc569-f83e-4779-9c1d-e4b219b89b55
```
Проверим:
http://nginx-example.34.90.132.76.xip.io/index.html
[nginx-example.PNG](./kubernetes-vault/screenshots/nginx-example.PNG)

## создадим CA на базе vault
Включим pki secrets
```
kubectl exec -it vault-0 -- vault secrets enable pki
kubectl exec -it vault-0 -- vault secrets tune -max-lease-ttl=87600h pki
kubectl exec -it vault-0 -- vault write -field=certificate pki/root/generate/internal common_name="exmaple.ru" ttl=87600h > CA_cert.crt
```
пропишем урлы для ca и отозванных сертификатов
```
kubectl exec -it vault-0 -- vault write pki/config/urls issuing_certificates="http://vault:8200/v1/pki/ca" crl_distribution_points="http://vault:8200/v1/pki/crl"
```
создадим промежуточный сертификат
```
kubectl exec -it vault-0 -- vault secrets enable --path=pki_int pki
kubectl exec -it vault-0 -- vault secrets tune -max-lease-ttl=87600h pki_int
kubectl exec -it vault-0 -- vault write -format=json pki_int/intermediate/generate/internal common_name="example.ru Intermediate Authority" | jq -r '.data.csr' > pki_intermediate.csr
```
пропишем промежуточный сертификат в vault
```
kubectl cp pki_intermediate.csr vault-0:/home/vault/
kubectl exec -it vault-0 -- vault write -format=json pki/root/sign-intermediate csr=@/home/vault/pki_intermediate.csr format=pem_bundle ttl=43800h | jq -r '.data.certificate' > intermediate.cert.pem
kubectl cp intermediate.cert.pem vault-0:/home/vault/
kubectl exec -it vault-0 -- vault write pki_int/intermediate/set-signed certificate=@/home/vault/intermediate.cert.pem
```
Создадим роль для выдачи с ертификатов
```
kubectl exec -it vault-0 -- vault write pki_int/roles/example-dot-ru allowed_domains="example.ru" allow_subdomains=true max_ttl="720h"
```
Создадим и отзовем сертификат
```
kubectl exec -it vault-0 -- vault write pki_int/issue/example-dot-ru common_name="gitlab.example.ru" ttl="24h"
kubectl exec -it vault-0 -- vault write pki_int/revoke serial_number="61:2d:12:b1:15:52:fb:ea:fa:19:cb:c2:e2:9b:b2:6e:5f:eb:14:2a"
```
выдача при создании и отзыве сертификата
```
dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform/kubernetes-vault (kubernetes-vault)
$ kubectl exec -it vault-0 -- vault write pki_int/issue/example-dot-ru common_name="gitlab.example.ru" ttl="24h"
Key                 Value
---                 -----
ca_chain            [-----BEGIN CERTIFICATE-----
MIIDnDCCAoSgAwIBAgIUbDpHTGseCXquA8kLUhj4evnPkmAwDQYJKoZIhvcNAQEL
BQAwFTETMBEGA1UEAxMKZXhtYXBsZS5ydTAeFw0yMDA4MDEyMzA3NDZaFw0yNTA3
MzEyMzA4MTZaMCwxKjAoBgNVBAMTIWV4YW1wbGUucnUgSW50ZXJtZWRpYXRlIEF1
dGhvcml0eTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKr+Yu+EtVM2
zwfYAaCQwqeNz3ClIw9adyXsb+jgq5fSQHudPxZDspc4wGSn5BbrHqjVk2Ql4w6n
iAkHZe+VyeIKhY9ROYlUnIuDF/HRkJAtZy7F9BjsEQNotNk0OtUJVIZcw8GQ+TG4
4vBXE/LYSGNdPLFx7rvoHuSHf/D2tOslF/dHgsBb2sCmqB1l8D5N7i2g9w72ue1O
Wrg1VA9R+2phHoqC2w6oGuZSoE21PsduDDEUhyK6o+c+DbKB2SLZsrhyPW+RPGPx
blw9Os/7KT3K5Hnfj5wsPn2JNWbBtzb82d4AVKACcaRd1drR70JIX/2w5uskMcUn
vpAeX6U26l8CAwEAAaOBzDCByTAOBgNVHQ8BAf8EBAMCAQYwDwYDVR0TAQH/BAUw
AwEB/zAdBgNVHQ4EFgQUVSjuONMEKAu+ZRoQRLwsthsXiGswHwYDVR0jBBgwFoAU
1M9t876191HIsihM1gU/ioslb38wNwYIKwYBBQUHAQEEKzApMCcGCCsGAQUFBzAC
hhtodHRwOi8vdmF1bHQ6ODIwMC92MS9wa2kvY2EwLQYDVR0fBCYwJDAioCCgHoYc
aHR0cDovL3ZhdWx0OjgyMDAvdjEvcGtpL2NybDANBgkqhkiG9w0BAQsFAAOCAQEA
KjGiFSuR09YnMGRWTEo2gBuUu+lG1pyDx6Jn+9haVuOvHWfROMSL0rcYaygOWl7g
+8T5MZcNZCbhnnEXJH3qn0v4WebwZaAcrjqVCarf7hFAQ3mNCPjA8qTLT3XJy/f9
LUr9VEsNa/jcpmiFzK05jcmWZHbf9PJ2w2jm0uYskJMtSjJ6PcramBdDOcB1FtMP
bmXPVbB7NMbosCTwDVsLlZUmlRYIoItp7XDYT41VuYS1gEAargV9jr94FPcvwlg6
fu5j6/aPTdgnzuQuFUF8CAQkROMFgGntJCEfajok4WmH8EqHQ33Cjs+RED62jYaO
aglLkubq8vxT+LjYEMz6Mg==
-----END CERTIFICATE-----]
certificate         -----BEGIN CERTIFICATE-----
MIIDZzCCAk+gAwIBAgIUYS0SsRVS++r6GcvC4puybl/rFCowDQYJKoZIhvcNAQEL
BQAwLDEqMCgGA1UEAxMhZXhhbXBsZS5ydSBJbnRlcm1lZGlhdGUgQXV0aG9yaXR5
MB4XDTIwMDgwMTIzMTUzOFoXDTIwMDgwMjIzMTYwN1owHDEaMBgGA1UEAxMRZ2l0
bGFiLmV4YW1wbGUucnUwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDV
asfM4q+3M5tAlbe5RJT45H7OWDIHhsUjd+8kw/XCvA7lOTTuKQ9TM3A2tsheD4RK
0GRObbSw2ZAphlWCHU0ABlx4iB/x6205DEbommsrdLVsjHey0G5Q4F4dAdq2krJB
x4NnTTvIAym+6MUsiKrb+DvD+X11nsAD17cVy4rASHHiG0uumw2mCVYAQOLF39zZ
FJx+HsTjJgPzv0o+q3pMjwhNSuTJIRF3U/vdavKRKEY9XfxNVZxkWmADKtER3FyK
VhY+Tmptg30HoihBWNqdtWaBDlNkjEyfHoxnX3Ti91Hg4aOojfT99qGFxb4cQX21
uuYCuYLmw7Fwnn3xOxVrAgMBAAGjgZAwgY0wDgYDVR0PAQH/BAQDAgOoMB0GA1Ud
JQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAdBgNVHQ4EFgQUSs6CBa1sq7w0oeNb
pgYIrAcd4b8wHwYDVR0jBBgwFoAUVSjuONMEKAu+ZRoQRLwsthsXiGswHAYDVR0R
BBUwE4IRZ2l0bGFiLmV4YW1wbGUucnUwDQYJKoZIhvcNAQELBQADggEBAIJLxuc1
KcuwbTJwu14UfKidTnZU235d6L/GtyEosJcPiLdwPFs4Rgn34ibOKB40HTQnoDgG
7+p3zJoJmsgPhwW2U6rjGTvOS4oHiflP5e8/p1nD1++X9ugh6sqSu8YnZuisjZHW
rz04dNA2jwOuvLjynMpAEwMVazxTOC/6SiLQO2EqBy2eT5/4UrAbjcdi1bfASSOe
tZB8P52YosaBi7cHjX/EsUGuH7LhaILYYKLRdzElPgcImQjiL8u7VQ6wFwS4+8oj
R0e8tFOSEQW/shWsUdxiVI52IYlnMpLqD7KOZ417J0jwurDxMQ40/pDKztToEupp
Nuvx22VkaFMQDTY=
-----END CERTIFICATE-----
expiration          1596410167
issuing_ca          -----BEGIN CERTIFICATE-----
MIIDnDCCAoSgAwIBAgIUbDpHTGseCXquA8kLUhj4evnPkmAwDQYJKoZIhvcNAQEL
BQAwFTETMBEGA1UEAxMKZXhtYXBsZS5ydTAeFw0yMDA4MDEyMzA3NDZaFw0yNTA3
MzEyMzA4MTZaMCwxKjAoBgNVBAMTIWV4YW1wbGUucnUgSW50ZXJtZWRpYXRlIEF1
dGhvcml0eTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAKr+Yu+EtVM2
zwfYAaCQwqeNz3ClIw9adyXsb+jgq5fSQHudPxZDspc4wGSn5BbrHqjVk2Ql4w6n
iAkHZe+VyeIKhY9ROYlUnIuDF/HRkJAtZy7F9BjsEQNotNk0OtUJVIZcw8GQ+TG4
4vBXE/LYSGNdPLFx7rvoHuSHf/D2tOslF/dHgsBb2sCmqB1l8D5N7i2g9w72ue1O
Wrg1VA9R+2phHoqC2w6oGuZSoE21PsduDDEUhyK6o+c+DbKB2SLZsrhyPW+RPGPx
blw9Os/7KT3K5Hnfj5wsPn2JNWbBtzb82d4AVKACcaRd1drR70JIX/2w5uskMcUn
vpAeX6U26l8CAwEAAaOBzDCByTAOBgNVHQ8BAf8EBAMCAQYwDwYDVR0TAQH/BAUw
AwEB/zAdBgNVHQ4EFgQUVSjuONMEKAu+ZRoQRLwsthsXiGswHwYDVR0jBBgwFoAU
1M9t876191HIsihM1gU/ioslb38wNwYIKwYBBQUHAQEEKzApMCcGCCsGAQUFBzAC
hhtodHRwOi8vdmF1bHQ6ODIwMC92MS9wa2kvY2EwLQYDVR0fBCYwJDAioCCgHoYc
aHR0cDovL3ZhdWx0OjgyMDAvdjEvcGtpL2NybDANBgkqhkiG9w0BAQsFAAOCAQEA
KjGiFSuR09YnMGRWTEo2gBuUu+lG1pyDx6Jn+9haVuOvHWfROMSL0rcYaygOWl7g
+8T5MZcNZCbhnnEXJH3qn0v4WebwZaAcrjqVCarf7hFAQ3mNCPjA8qTLT3XJy/f9
LUr9VEsNa/jcpmiFzK05jcmWZHbf9PJ2w2jm0uYskJMtSjJ6PcramBdDOcB1FtMP
bmXPVbB7NMbosCTwDVsLlZUmlRYIoItp7XDYT41VuYS1gEAargV9jr94FPcvwlg6
fu5j6/aPTdgnzuQuFUF8CAQkROMFgGntJCEfajok4WmH8EqHQ33Cjs+RED62jYaO
aglLkubq8vxT+LjYEMz6Mg==
-----END CERTIFICATE-----
private_key         -----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA1WrHzOKvtzObQJW3uUSU+OR+zlgyB4bFI3fvJMP1wrwO5Tk0
7ikPUzNwNrbIXg+EStBkTm20sNmQKYZVgh1NAAZceIgf8ettOQxG6JprK3S1bIx3
stBuUOBeHQHatpKyQceDZ007yAMpvujFLIiq2/g7w/l9dZ7AA9e3FcuKwEhx4htL
rpsNpglWAEDixd/c2RScfh7E4yYD879KPqt6TI8ITUrkySERd1P73WrykShGPV38
TVWcZFpgAyrREdxcilYWPk5qbYN9B6IoQVjanbVmgQ5TZIxMnx6MZ1904vdR4OGj
qI30/fahhcW+HEF9tbrmArmC5sOxcJ598TsVawIDAQABAoIBAQChTD8N/xZHJF3m
hkGBaPAe3LNqSQYm4hkFIZRA+Uo5j+DCJmZ2ydmnTG03LRZq4Ndfo/jrvcafEw/+
EmV2Hacgqa4h+uAJ+6FlSH4fNvZgtaiZDeE56IY34hu/WLNw4ZaQWLZb0Oep15op
i8vaSMC51/dzupCz4PPG87aQZnHLuJPJTO1c7ruK15H/UH2r0rqLnzEe13RCZjds
1XQmgaGt+DCriODZb1+UPHnLk0eSeT8tJ01/6SN0QukBoMr2xWQjlxU6nwYLQmgj
SAahppZfLU5cBUlYzQHiu1Mb5M1E25LzFHSIaq7nfL3Q9BCW1T8GSDjFUwPEV5Jg
S2RdnRKhAoGBAO/f5IH0E22EWq4SX1ao5wh5yAe0Z0KUCn53FnCWpUfs9zCAPhqC
Xpuv9/3RSIHBSDMjdO9UbG9y3Qr+6n4VD9Gcj/UO974dcNceWYeY36I28qR3FNFh
tLrDQMdIYQq1T1WOOqht2lMcsLvUzCjXxZeu4LeS3prIvfnN+ewrAGNVAoGBAOPD
kdICVBA3FXtNB0AtgjvvMswpaVjepsoWJ+JBuPWoSszDQ22gYMsPGJtfXEofcYES
ZJ+H5VVk5cShTG+PfxBkUeDXFQK3WveVY8hc/P4823RxxzPASCoZkgiP5GwSXOE6
ExXKTcxVBpvgzb9NbRYyzttyDC/LruUuA7SanxW/AoGAS59FFecRvOQOBnTKU7K5
60UhV7R7HVU4nbgDfgkwICXHpCW57neNRf3K69zvw+BgV6bk9ZKjANuwbggBezA+
pXF7POG0Ht5/NYJe7U23qxcxlcHo8T2hUYO+x1S9KzgPw8QsH+9J9gvEd+LVXkbw
Byrds2H9BcUlhzx1fwvremUCgYAM1Z9o8yKji0cVnKCU+DuHfxIguRCrplhFuPvk
Xwm6JhKY+UPacJgjuSUM1FHSB3WQ7WVoK/M7XaUo8GHrQ23Ika6fed9AOO7SVsO5
rau/89P1+tdbzjEC1lAJVXpssJg1RN2Ac9bwdbYaoI9XgVhtUM2hRgrzwomHdpFU
4wWl5wKBgApGlUnhHtB6USHSiQ69UL3DwAVOFd7LBaE0egg2H+xTdR8lOWT6RjL4
jkdUolHG0Ce+e8RbmRzCqNWV5Ordgvr0DOI5lhsTsJQool6B7gfGP46BWH214lm3
i+yk9AtBXB/4eNcxu8qFmdowhEK0M+pGfEnIHIywnppACJb4rVJa
-----END RSA PRIVATE KEY-----
private_key_type    rsa
serial_number       61:2d:12:b1:15:52:fb:ea:fa:19:cb:c2:e2:9b:b2:6e:5f:eb:14:2a

dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform/kubernetes-vault (kubernetes-vault)
$ kubectl exec -it vault-0 -- vault write pki_int/revoke serial_number="61:2d:12:b1:15:52:fb:ea:fa:19:cb:c2:e2:9b:b2:6e:5f:eb:14:2a"
Key                        Value
---                        -----
revocation_time            1596323871
revocation_time_rfc3339    2020-08-01T23:17:51.880591603Z
```
## включить TLS

Сгенерим private key, и запрос на подпись и посмотрим результат:
```
openssl genrsa -out vault_gke.key 4096
openssl req -config vault_gke_csr.cnf -new -key vault_gke.key -nodes -out vault.csr
openssl req -text -noout -in vault.csr
```
сделаем CertificateSigningRequest чтобы Kubernetes подписал наш сертификат. Проапрувим и посмотрим получившийся сертификат. Сертификаты положим в secret.
```
export BASE64_CSR=$(cat vault.csr | base64 | tr -d '\n')
cat certificate-signing-request.yaml | envsubst | kubectl apply -f -export BASE64_CSR=$(cat vault.csr | base64 | tr -d '\n')
kubectl certificate approve vaultcsr
kubectl get csr vaultcsr -o jsonpath='{.status.certificate}'  | base64 --decode > vault.crt
kubectl create secret tls vault-certs --cert=vault.crt --key=vault_gke.key       
openssl x509 -in vault.crt -text -noout                                                             cat certificate-signing-request.yaml | envsubst | kubectl apply -f -
```

обновим Vault указав секрет (см https.vault.values.yaml)
```
helm upgrade --install vault ../vault-helm -f kubernetes-vault/https.vault.values.yaml
```
проверка https://vault.34.90.132.76.xip.io/ui/vault/auth?with=token
root token s.wHTxv9lhN5QKQc3erpBQRsqq
[vault_cert.PNG](./kubernetes-vault/screenshots/vault_cert.PNG)

# Выполнено ДЗ № 9

 - [ ] Основное ДЗ
 

## В процессе сделано:
 - Создан GKE кластер, 4 ноды.
 ```text
   $ kubectl get nodes
   NAME                                             STATUS   ROLES    AGE   VERSION
   gke-cluster-logging-default-pool-2baa7f86-fqmb   Ready    <none>   27h   v1.15.9-gke.24
   gke-cluster-logging-infra-pool-94a26708-1xdq     Ready    <none>   27h   v1.15.9-gke.24
   gke-cluster-logging-infra-pool-94a26708-gcpw     Ready    <none>   27h   v1.15.9-gke.24
   gke-cluster-logging-infra-pool-94a26708-rhvx     Ready    <none>   27h   v1.15.9-gke.24
```
 - на кластере отключен Stackdriver, для нод infra-pool выставлен taint
 ```text
kubectl taint nodes gke-cluster-logging-infra-pool-94a26708-1xdq node-role=infra:NoSchedule
kubectl taint nodes gke-cluster-logging-infra-pool-94a26708-gcpw node-role=infra:NoSchedule
kubectl taint nodes gke-cluster-logging-infra-pool-94a26708-rhvx node-role=infra:NoSchedule
```
 - Устанавливаем Hipster Shop на default-pool ноду
 - Устанавливаем elasticsearch, kibana, fluent-bit, в манифестах указываем tolerations
```text
helm upgrade --install elasticsearch elastic/elasticsearch --namespace observability -f elasticsearch.values.yaml
helm upgrade --install kibana elastic/kibana --namespace observability -f kibana.values.yaml
helm upgrade --install fluent-bit stable/fluent-bit --namespace observability -f fluent-bit.values.yaml
```
 - устанавливаем nginx-ingress controller
 ```text
kubectl create ns nginx-ingress
helm upgrade --install nginx-ingress stable/nginx-ingress --wait --namespace=nginx-ingress --version=1.11.1 -f ingress.values.yaml
```
- обновляем kibana, смотрим http://kibana.35.193.244.77.xip.io/app/kibana#/home
- чиним fluent-bit (time и timestamp), чиним логи от nginx ingress 
- ставим Prometheus и Grafana
```text
helm upgrade --install prometheus-operator stable/prometheus-operator --set prometheusOperator.createCustomResource=false -f prometheus-operator.values.yaml -n observability
helm upgrade --install elasticsearch-exporter stable/elasticsearch-exporter --set es.uri=http://elasticsearch-master:9200 --set serviceMonitor.enabled=true --namespace=observability
```
- Импортируем Dashboard [grafana_elasticsearch.PNG](./kubernetes-logging/screenshots/grafana_elasticsearch.PNG) 
- Добавили alert ElasticsearchTooFewNodesRunning 
- Настраиваем Dashboard в Kibana [dashboard.PNG](./kubernetes-logging/screenshots/dashboard.PNG)
- Ставим Loki
```text
helm repo add loki https://grafana.github.io/loki/charts
helm repo update
helm upgrade --install loki loki/loki-stack --namespace observability -f loki.values.yaml
```
- Создаем Dashboard [loki.PNG](./kubernetes-logging/screenshots/loki.PNG)

## Как запустить проект:
 - выполнить helm charts

## Как проверить работоспособность:
 - http://kibana.35.193.244.77.xip.io/
 - http://prometheus.35.193.244.77.xip.io/
 - http://grafana.35.193.244.77.xip.io/

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания



# Выполнено ДЗ № 8
 - [ ] Основное ДЗ

## В процессе сделано:
 - Установлен Prometheus Operator чезез Helm 3
 - Создан Deployment c 3 репликами nginx + nginx exporter
 - Проверено, что метрики видны в Prometheus и Grafana 

## Как запустить проект:
 - Использовался Kind c 3мя нодами.
 - готовим nginx-with-metrics
   - собираем образ nginx с включенным ngx_http_stub_status_module.  (./nginx/push.sh)
   - деплоим в docker hub, проверяем:
   - ``docker run -p 80:80 dimpon/nginx-with-metrics:1.0``
   - статистика должна быть доступна по http://localhost/basic_status
 - создаем манифесты для deployment, service, service-monitor
 - Prometheus Operator
   - ``cd prometheus``
   - ``crd.sh`` //создаем CRD
   - деплоим через Helm 3, используем кастомный values.yaml
   ```
     helm repo add stable https://kubernetes-charts.storage.googleapis.com
     kubectl create ns monitoring
     helm upgrade --install prometheus-monitor stable/prometheus-operator -n monitoring -f values.yaml --set prometheusOperator.createCustomResources=false
     ```
    - прверяем:
    ```
     kubectl port-forward prometheus-monitor-grafana-54b6699f56-hb7nf  -n monitoring 3000:3000
     kubectl port-forward prometheus-prometheus-monitor-prometh-prometheus-0 -n monitoring 9090:9090
   ```
  - деплоим nginx-with-metrics: ``deploy.sh``
   - заходим на одну из нод:
     ``docker exec -it <container> bash``
     дергаем несколько раз nginx:
     ```
     root@kind-worker:/# curl http://10.111.238.58
     <!DOCTYPE html>
     <html lang="en">
     <head>
         <meta charset="UTF-8">
         <title>Title</title>
     </head>
     <body>
     Hello, that is nginx http endpoint. I'm alive.
     </body>
     </html>
     ```
     
     - install goldpinger
       ``helm upgrade --install goldpinger stable/goldpinger``
     - проверяем в Prometheus и Grafana и Goldpinger:
        * [prometheus.PNG](./kubernetes-monitoring/screenshots/prometheus.PNG) 
        * [grafana.PNG](./kubernetes-monitoring/screenshots/grafana.PNG)
        * [goldpinger.PNG](./kubernetes-monitoring/screenshots/goldpinger.PNG)
     

## Как проверить работоспособность:
 - kubectl port-forward prometheus-monitor-grafana-54b6699f56-hb7nf -n monitoring 3000:3000
 - kubectl port-forward prometheus-prometheus-monitor-prometh-prometheus-0 -n monitoring 9090:9090
 - open [Prometheus](http://localhost:9090/graph?g0.range_input=1h&g0.expr=rate(nginx_http_requests_total%5B1m%5D)&g0.tab=0)
 - open [Grafana](http://localhost:3000/explore?orgId=1&left=%5B%22now-1h%22,%22now%22,%22Prometheus%22,%7B%22expr%22:%22rate(nginx_http_requests_total%5B1m%5D)%22%7D,%7B%22mode%22:%22Metrics%22%7D,%7B%22ui%22:%5Btrue,true,true,%22none%22%5D%7D%5D)

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания

# Выполнено ДЗ № 7

 - [ ] Основное ДЗ создать CRD,починить валидацию, и написать оператор на Python, сделать Docker image, задерлоить как Deployment
 - [ ] Задание со * настроить status subresource, написать ф-ю обработки изменений 

## В процессе сделано:
 - Создан CRD, создан ресурс, написан оператор, делан Docker image, оператор задеплоен как Pod
 - Выполнены задания с *
 

## Как запустить проект:
 - Запустить [build/push.sh](kubernetes-operators/build/push.sh), затем применить манифесты из deploy.
    - role.yml
    - role-binding.yml
    - service-account.yml
    - deploy-operator.yml
    - crd.yml
    - cr.yml
 - Проверить базу :
```
export MYSQLPOD=$(kubectl get pods -l app=mysql-instance -o jsonpath="{.items[*].metadata.name}")
kubectl exec -it $MYSQLPOD -- mysql -u root -potuspassword -e "CREATE TABLE test (id smallint unsigned not null auto_increment, name varchar(20) not null, constraint pk_example primary key (id) );" otus-database
kubectl exec -it $MYSQLPOD -- mysql -potuspassword -e "INSERT INTO test ( id, name) VALUES ( null, 'some data' );" otus-database
kubectl exec -it $MYSQLPOD -- mysql -potuspassword -e "INSERT INTO test ( id, name ) VALUES ( null, 'some data-2' );" otus-database

kubectl exec -it $MYSQLPOD -- mysql -potuspassword -e "select * from test;" otus-database
```

## Как проверить работоспособность:
``` 
$ kubectl api-resources | grep mysql
mysqls                            ms           otus.homework                  true         MySQL

$ kubectl get ms
NAME             AGE
mysql-instance   18h

$ kubectl get pvc
NAME                        STATUS   VOLUME                     CAPACITY   ACCESS MODES   STORAGECLASS            AGE
backup-mysql-instance-pvc   Bound    backup-mysql-instance-pv   1Gi        RWO            backup-mysql-instance   13s
mysql-instance-pvc          Bound    mysql-instance-pv          1Gi        RWO            mysql-instance          13s

$ kubectl get all
NAME                                   READY   STATUS             RESTARTS   AGE
pod/mysql-instance-f5b97ffff-q8jfk     1/1     Running            0          2m26s
pod/restore-mysql-instance-job-dw244   0/1     CrashLoopBackOff   4          2m25s

NAME                     TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
service/kubernetes       ClusterIP   10.96.0.1    <none>        443/TCP    25h
service/mysql-instance   ClusterIP   None         <none>        3306/TCP   2m26s

NAME                             READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/mysql-instance   1/1     1            1           2m26s

NAME                                       DESIRED   CURRENT   READY   AGE
replicaset.apps/mysql-instance-f5b97ffff   1         1         1       2m26s

NAME                                   COMPLETIONS   DURATION   AGE
job.batch/restore-mysql-instance-job   0/1           2m25s      2m25s
```
база работает:
```
$ kubectl exec -it $MYSQLPOD -- mysql -potuspassword -e "select * from test;" otus-database
mysql: [Warning] Using a password on the command line interface can be insecure.
+----+-------------+
| id | name        |
+----+-------------+
|  1 | some data   |
|  2 | some data-2 |
+----+-------------+
```
ресурс mysql удалили, создали - база жива
```
$ kubectl exec -it $MYSQLPOD -- mysql -potuspassword -e "select * from test;" otus-database
mysql: [Warning] Using a password on the command line interface can be insecure.
+----+-------------+
| id | name        |
+----+-------------+
|  1 | some data   |
|  2 | some data-2 |
+----+-------------+
```
создаем Docker image push.sh, прогоняем манифесты, повторяем проверку базы - жива
```
dimpo@DESKTOP-SN07QBO MINGW64 /d/projects/k8s_study/dimpon_platform/kubernetes-operators/deploy (kubernetes-operators)
$ kubectl exec -it $MYSQLPOD -- mysql -potuspassword -e "select * from test;" otus-database
mysql: [Warning] Using a password on the command line interface can be insecure.
+----+-------------+
| id | name        |
+----+-------------+
|  1 | some data   |
|  2 | some data-2 |
+----+-------------+

$ kubectl get jobs
NAME                         COMPLETIONS   DURATION   AGE
backup-mysql-instance-job    1/1           2s         5m25s
restore-mysql-instance-job   1/1           53s        4m11s
```

##Задание со * 
манифесты и оператор в папке [asterisks](kubernetes-operators/asterisks). (mysql решил не трогать, тк мои прошлые оптимизации оператора привели к поломке travis)
Чтобы начать писать в subresources status достаточно в CRD manifest добавить:
```yaml
  subresources:
    status: {}
```
а в ф-ях Kopf возвращать значение:
```python
@kopf.on.create('example.dimpon.com', 'v1', 'dogs')
def dog_on_create(spec, name, status, namespace, logger, **kwargs):
    logger.info("dog is creating... name:%s spec:%s  status:%s namespace:%s ", name, spec, status, namespace)
    message = name + " dog is owned by " + spec['owner']
    return {'message': message}
```
тогда:
```yaml
$ kubectl get dogs polkan -o yaml
apiVersion: example.dimpon.com/v1
kind: Dog
metadata:
  name: polkan
  namespace: default
  resourceVersion: "21504"
:
:
:
spec:
  owner: John Dou
status:
  dog_on_create:
    message: polkan dog is owned by Vasya Petrov
  dog_on_update:
    message: polkan dog is owned by John Dou

```
чтобы перхватывать обновление ресурса делаем новый метод:
```python
@kopf.on.update('example.dimpon.com', 'v1', 'dogs')
def dog_on_update(spec, name, status, namespace, logger, **kwargs):
    logger.info("dog is updating... name:%s spec:%s  status:%s namespace:%s ", name, spec, status, namespace)
    message = name + " dog is owned by " + spec['owner']
    return {'message': message}
```
в нем есть вся необходимая информация для пересоздания deployment и других ресурсов. Если взять наше исходное задание, то легко пересоздать deployment с новым паролем или именем базы. 
лог оператора:
```text
[2020-07-04 19:50:41,714] kopf.objects         [INFO    ] [default/polkan] dog is creating... name:polkan spec:{'owner': 'Vasya Petrov'}  status:{} namespace:default
[2020-07-04 19:50:41,719] kopf.objects         [INFO    ] [default/polkan] Handler 'dog_on_create' succeeded.
[2020-07-04 19:50:41,720] kopf.objects         [INFO    ] [default/polkan] All handlers succeeded for creation.
[2020-07-04 19:51:30,485] kopf.objects         [INFO    ] [default/polkan] dog is updating... name:polkan spec:{'owner': 'John Dou'}  status:{'dog_on_create': {'message': 'polkan dog is owned by Vasya Petrov'}} namespace:default
[2020-07-04 19:51:30,491] kopf.objects         [INFO    ] [default/polkan] Handler 'dog_on_update' succeeded.
[2020-07-04 19:51:30,495] kopf.objects         [INFO    ] [default/polkan] All handlers succeeded for update.
```

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания



# Выполнено ДЗ № 6

 - [ ] Основное ДЗ:
      * Создать кластер на GCP,  настроить клиента
      *  Используя готовые Helm charts установить:
            * nginx-ingress
            * cert-manager
            * chartmuseum
            * harbor
      * Создать свой helm chart, задеплоить hipster-shop
      * Работа с helm-secrets | Необязательное задание
      * Kubecfg
      * Kustomize

 

## В процессе сделано:
 - Создан кластер на GCP,  настроен клиент
 - установлен harbor 3
 - установлены 
   * nginx-ingress
   * cert-manager (дополнительно создан ClusterIssuer)
   * chartmuseum [screen](./screens/chartmuseum.png) 
   * harbor  [screen](./screens/harbor.png)
```text
kubectl create ns nginx-ingress
helm upgrade --install nginx-ingress stable/nginx-ingress --wait --namespace=nginx-ingress --version=1.11.1

kubectl create ns cert-manager
helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v0.15.1 --set installCRDs=true

kubectl apply -f cluster-issuer.yaml

kubectl create ns chartmuseum
helm upgrade --install chartmuseum stable/chartmuseum --wait --namespace=chartmuseum --version=2.3.2 -f kubernetes-templating/chartmuseum/values.yaml

helm install 1.1.2 harbor/harbor
kubectl create ns harbor
helm upgrade --install harbor harbor/harbor --wait --namespace=harbor --version=1.1.2 -f values.yaml
```
 - задание с (*)   
 ```text
* как работаь с chartmuseum.
chartmuseum предоствляет REST API

делаем tgz
helm package .

заливаем на chartmuseum
curl --data-binary "@mychart-0.1.0.tgz" https://chartmuseum.34.78.246.165.nip.io/api/charts

смотрим
curl https://chartmuseum.34.78.246.165.nip.io/api/charts

добавляем repo в локальный helm
helm repo add chartmuseum https://chartmuseum.34.78.246.165.nip.io
```

 - создан helm chart с all-hipster-shop.yaml
 - frontend вынесен в отдельный all-hipster-shop.yaml, создан Ingress (https://shop.34.78.246.165.nip.io/)
 - helm chart с frontend шаблонизирован, добавлен как dependency в Chart.yaml
 - задание с (*)  создан helm chart с redis, шаблонизирован, добавлен как dependency в requirements.yaml
 - Работа с helm-secrets пропущена
 - paymentservice и shippingservice шаблонизированы с помощью Kubecfg
 - recommendationservice шаблонизированы с помощью Kustomize

  
## Как запустить проект:
```text
kubectl create ns nginx-ingress
helm upgrade --install nginx-ingress stable/nginx-ingress --wait --namespace=nginx-ingress --version=1.11.1

kubectl create ns cert-manager
helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v0.15.1 --set installCRDs=true

kubectl apply -f cluster-issuer.yaml

kubectl create ns chartmuseum
helm upgrade --install chartmuseum stable/chartmuseum --wait --namespace=chartmuseum --version=2.3.2 -f kubernetes-templating/chartmuseum/values.yaml

helm install 1.1.2 harbor/harbor
kubectl create ns harbor
helm upgrade --install harbor harbor/harbor --wait --namespace=harbor --version=1.1.2 -f values.yaml

kubectl create ns hipster-shop
helm upgrade --install hipster-shop kubernetes-templating/hipster-shop --namespace hipster-shop
helm upgrade --install frontend kubernetes-templating/frontend --namespace hipster-shop
helm delete frontend -n hipster-shop
helm dep update kubernetes-templating/hipster-shop

* вынесем redis и пропишем в requirements.yaml
helm create kubernetes-templating/redis
helm upgrade --install redis kubernetes-templating/redis --namespace hipster-shop

kubecfg show services.jsonnet

kustomize build ./overrides/hipster-shop >staging.yaml
kustomize build ./overrides/hipster-shop-prod/ >prod.yaml
```

## Как проверить работоспособность:
 - https://chartmuseum.34.78.246.165.nip.io/
 - https://harbor.34.78.246.165.nip.io/
 - http://shop.34.78.246.165.nip.io/
 ```text
kubecfg show services.jsonnet

kustomize build ./overrides/hipster-shop >staging.yaml
kustomize build ./overrides/hipster-shop-prod/ >prod.yaml
```

## PR checklist:
 - [ ] Выставлен label с темой домашнего задания


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
