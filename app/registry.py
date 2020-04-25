import requests

def mk_tenant(url, tenant_id):
    url += "v1/tenants/" + tenant_id
    res = requests.post(url)
    if res.status_code == 201 or res.status_code == 409:
        return tenant_id
    raise Exception("Bad request.")

def rm_tenant(url, tenant_id):
    url += "v1/tenants/" + tenant_id
    requests.delete(url)

def mk_device(url, tenant_id, dev_id):
    url += "v1/devices/%s/%s" % (tenant_id, dev_id)
    res = requests.post(url)
    if res.status_code == 201 or res.status_code == 409:
        return dev_id
    raise Exception("Bad request")

def set_passwd(url, tenant_id, dev_id, auth_id, passwd):
    url += "v1/credentials/%s/%s" % (tenant_id, dev_id)
    payload = [{
        "type": "hashed-password",
        "auth-id": auth_id,
        "secrets": [{"pwd-plain": passwd}]
    }]
    res = requests.put(url, json=payload)
    if res.status_code == 204:
        return
    raise Exception("Bad request.")

def rm_device(url, tenant_id, dev_id):
    url += "v1/devices/%s/%s" % (tenant_id, dev_id)
    requests.delete(url)

def mk_api_factory(host, port):
    url = "http://%s:%d/" % (host, port)
    def create(handler, url=url):
        def call(*args, handler=handler, url=url):
            return handler(url, *args)
        return call
    return create
