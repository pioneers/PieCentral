def uid_to_device_id(uid, num_devices):
    return [str(uid) + str(device_index) for device_index in range(num_devices)]

def device_id_to_uid(device_id):
    return device_id[:-1]
