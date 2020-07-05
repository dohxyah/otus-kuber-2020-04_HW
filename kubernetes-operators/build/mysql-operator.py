import kopf
import yaml
import kubernetes
import time
from jinja2 import Environment, FileSystemLoader
import logging

# ждем завершения Job
def wait_until_job_end(jobname):
    api = kubernetes.client.BatchV1Api()
    job_finished = False
    jobs = api.list_namespaced_job('default')
    while (not job_finished) and \
            any(job.metadata.name == jobname for job in jobs.items):
        time.sleep(1)
        jobs = api.list_namespaced_job('default')
        for job in jobs.items:
            if job.metadata.name == jobname:
                if job.status.succeeded == 1:
                    job_finished = True

def render_template(filename, vars_dict):
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template(filename)
    yaml_manifest = template.render(vars_dict)
    json_manifest = yaml.load(yaml_manifest, Loader=yaml.FullLoader)
    return json_manifest

# удаляем отработавший job
def delete_success_jobs(mysql_instance_name):
    api = kubernetes.client.BatchV1Api()
    jobs = api.list_namespaced_job('default')
    for job in jobs.items:
        jobname = job.metadata.name
        if (jobname == f"backup-{mysql_instance_name}-job") or \
                (jobname == f"restore-{mysql_instance_name}-job"):
            if job.status.succeeded == 1:
                api.delete_namespaced_job(jobname, 'default', propagation_policy='Background')



# Функция, которая будет запускаться при создании объектов тип MySQL:
@kopf.on.create('otus.homework', 'v1', 'mysqls')
def mysql_on_create(body, spec, **kwargs):
    logging.info("Mysql is creating...")
    logging.debug(body)

    # cохраняем в переменные содержимое описания MySQL из CR
    name = body['metadata']['name']
    image = body['spec']['image']
    password = body['spec']['password']
    database = body['spec']['database']
    storage_size = body['spec']['storage_size']

    # Генерируем JSON манифесты для деплоя
    logging.info("Generating manifests...")
    persistent_volume = render_template('mysql-pv.yml.j2', {'name': name, 'storage_size': storage_size})
    persistent_volume_claim = render_template('mysql-pvc.yml.j2', {'name': name, 'storage_size': storage_size})
    service = render_template('mysql-service.yml.j2', {'name': name})
    deployment = render_template('mysql-deployment.yml.j2', {
        'name': name,
        'image': image,
        'password': password,
        'database': database})
    restore_job = render_template('restore-job.yml.j2', {
        'name': name,
        'image': image,
        'password': password,
        'database': database})

    logging.debug("manifests:")
    logging.debug(persistent_volume)
    logging.debug(persistent_volume_claim)
    logging.debug(service)
    logging.debug(deployment)
    logging.debug(restore_job)

    # Определяем, что созданные ресурсы являются дочерними к управляемому CustomResource:
    logging.info("Set resources dependant from mysql...")
    kopf.append_owner_reference(persistent_volume, owner=body)
    kopf.append_owner_reference(persistent_volume_claim, owner=body)
    kopf.append_owner_reference(service, owner=body)
    kopf.append_owner_reference(deployment, owner=body)
    # ^ Таким образом при удалении CR удалятся все, связанные с ним pv,pvc,svc, deployments


    api = kubernetes.client.CoreV1Api()
    # Создаем mysql PV:
    api.create_persistent_volume(persistent_volume)
    # Создаем mysql PVC:
    api.create_namespaced_persistent_volume_claim('default', persistent_volume_claim)
    # Создаем mysql SVC:
    api.create_namespaced_service('default', service)

    # Создаем mysql Deployment:
    api = kubernetes.client.AppsV1Api()
    api.create_namespaced_deployment('default', deployment)

    message = name + " Deployment is created"

    try:
        backup_pv = render_template('backup-pv.yml.j2', {'name': name})
        api = kubernetes.client.CoreV1Api()
        api.create_persistent_volume(backup_pv)
        logging.info("backup-pv is created")
    except kubernetes.client.rest.ApiException:
        pass

    try:
        backup_pvc = render_template('backup-pvc.yml.j2', {'name': name})
        api = kubernetes.client.CoreV1Api()
        api.create_namespaced_persistent_volume_claim('default', backup_pvc)
        logging.info("backup-pvc is created")
    except kubernetes.client.rest.ApiException:
        pass

    # Пытаемся восстановиться из backup
    try:
        api = kubernetes.client.BatchV1Api()
        api.create_namespaced_job('default', restore_job)
        message += " with restore job"
        logging.info("Restored from backup")
    except kubernetes.client.rest.ApiException:
        message += " without restore job"
        pass

    logging.info(message)

    return {'message': message}

# Функция, которая будет запускаться при удалении объектов тип MySQL:
@kopf.on.delete('otus.homework', 'v1', 'mysqls')
def delete_object_make_backup(body, **kwargs):
    name = body['metadata']['name']
    image = body['spec']['image']
    password = body['spec']['password']
    database = body['spec']['database']
    logging.info("Deleting mysql: "+name)

    logging.info("Going to delete old jobs...")
    delete_success_jobs(name)

    logging.info("Going to run backup job...")
    # Cоздаем backup job:
    api = kubernetes.client.BatchV1Api()
    backup_job = render_template('backup-job.yml.j2', {
        'name': name,
        'image': image,
        'password': password,
        'database': database})
    api.create_namespaced_job('default', backup_job)
    wait_until_job_end(f"backup-{name}-job")

    return {'message': "mysql and its children resources deleted"}


@kopf.on.update('otus.homework', 'v1', 'mysqls')
def update_object(body, **kwargs):
    logging.info("update "+body)
    return {'message': "mysql updated"}

