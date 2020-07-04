import kopf


@kopf.on.create('example.dimpon.com', 'v1', 'dogs')
def dog_on_create(spec, name, status, namespace, logger, **kwargs):
    logger.info("dog is creating... name:%s spec:%s  status:%s namespace:%s ", name, spec, status, namespace)
    message = name + " dog is owned by " + spec['owner']
    return {'message': message}


@kopf.on.update('example.dimpon.com', 'v1', 'dogs')
def dog_on_update(spec, name, status, namespace, logger, **kwargs):
    logger.info("dog is updating... name:%s spec:%s  status:%s namespace:%s ", name, spec, status, namespace)
    message = name + " dog is owned by " + spec['owner']
    return {'message': message}
