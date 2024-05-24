import requests
import urllib3
import json
import config
import sys
import ipaddress
from requests.auth import HTTPBasicAuth
import logging
from logging import StreamHandler, Formatter
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = StreamHandler(stream=sys.stdout)
urllib3.disable_warnings()
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)
SESSION = ''


def update_session_id(user, password, hostname):
    global SESSION
    while True:
        url = "https://%s:%s@%s/api" % (user, password, hostname)
        headers = {"Cookie": "timezone=Europe%sMoscow; _session_id=%s" %
                   ('%2F', SESSION)}
        try:
            r = requests.get(url='https://%s/api' % hostname,
                             headers=headers, verify=config.VEREFY).json()
        except:
            continue
        if 'error' not in r.keys():
            return SESSION
        else:
            try:
                res = requests.get(url=url, headers=headers,
                                   verify=config.VEREFY)
                SESSION = res.cookies['_session_id']
            except:
                continue


def get_template_kind_id(id):
    global SESSION
    uri = '/api/provisioning_templates/%s' % id
    url = 'https://%s%s' % (config.FOREMAN_HOST, uri)
    headers = {"Cookie": "timezone=Europe%sMoscow; _session_id=%s" %
               ('%2F', SESSION)}
    res = requests.get(url=url, verify=config.VEREFY, headers=headers).json()
    return res['template_kind_id']


def get_id_name(name, method):
    global SESSION
    uri = '/api/%s' % method
    uri_search = '%s?search=%s' % (uri, name)
    url = 'https://%s%s' % (config.FOREMAN_HOST, uri_search)
    headers = {"Cookie": "timezone=Europe%sMoscow; _session_id=%s" %
               ('%2F', SESSION)}
    res = requests.get(url=url, verify=config.VEREFY, headers=headers).json()
    if len(res['results']) > 0:
        for i in res['results']:
            if i['name'] == name:
                return i['id']


def change_global_root_pass(new_pass):
    # global SESSION
    uri = '/api/settings/root_pass'
    url = 'https://%s%s' % (config.FOREMAN_HOST, uri)
    data = {"setting": {"value": new_pass}}
    data = json.dumps(data)
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth(config.FOREMAN_USER, config.FOREMAN_PASSWORD)
    r = requests.put(url=url, verify=config.VEREFY,
                     headers=headers, data=data, auth=auth)
    if r.status_code >= 200 and r.status_code <= 299:
        logger.info('change_global_root_pass - ok')
    else:
        logger.error(r.text)


def create_host(name='ubuntu-demo', organization_id=1, location_id=2, architecture_id=1, operatingsystem_id=1, medium_id=17, ptable_id=131, pxe_loader='PXELinux BIOS', domain_id=1, subnet_os_id=1, subnet_pxe_id=2, mac="080027C88C03", os_ip="192.168.1.42"):
    uri = '/api/hosts'
    url = 'https://%s%s' % (config.FOREMAN_HOST, uri)
    data = {
        "host": {
            "name": name,
            "build": True,
            "organization_id": organization_id,
            "location_id": location_id,
            "managed": True,
            "architecture_id": architecture_id,
            "operatingsystem_id": operatingsystem_id,
            "medium_id": medium_id,
            "ptable_id": ptable_id,
            "pxe_loader": pxe_loader,
            "interfaces_attributes": [
                {
                    'type': 'interface',
                    'mac': mac,
                    'ip': os_ip,
                    'name': name,
                    'subnet_id': subnet_os_id,
                    'domain_id': domain_id,
                    'primary': True,
                    'managed': False,
                    'provision': False
                },
                {
                    'type': 'interface',
                    'mac': mac,
                    'name': '%s-pxe' % name,
                    'subnet_id': subnet_pxe_id,
                    'domain_id': domain_id,
                    'managed': True,
                    'provision': True,
                    'primary': False
                },
            ]
        }
    }

    data = json.dumps(data)
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth(config.FOREMAN_USER, config.FOREMAN_PASSWORD)
    r = requests.post(url=url, verify=config.VEREFY,
                      headers=headers, data=data, auth=auth)
    if r.status_code >= 200 and r.status_code <= 299:
        logger.info('create host - %s' % name)
        return True
    else:
        logger.info(r.text)
        logger.info('not need create host - %s' % name)
        return False


def create_media(name, foreman_proxy_ip, location_ids=[2], organization_ids=[1]):
    # global SESSION
    uri = '/api/media'
    uri_search = '%s?search=%s' % (uri, name)
    url = 'https://%s%s' % (config.FOREMAN_HOST, uri)
    data = {
        "medium": {
            "name": name,
            "path": "http://%s:8000/EFI/ubuntu-20.04.6-live-server-amd64" % foreman_proxy_ip,
            "location_ids": location_ids,
            "organization_ids": organization_ids,
            "os_family": "Debian"
        }
    }
    data = json.dumps(data)
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth(config.FOREMAN_USER, config.FOREMAN_PASSWORD)
    r = requests.post(url=url, verify=config.VEREFY,
                      headers=headers, data=data, auth=auth)
    if r.status_code >= 200 and r.status_code <= 299:
        logger.info('create media - %s' % name)
    else:
        logger.error(r.text)


def import_template(template_name, location_ids=[2], organization_ids=[1]):
    uri = '/api/provisioning_templates/import'
    url = 'https://%s%s' % (config.FOREMAN_HOST, uri)
    file = open(template_name, 'r')
    f = file.read()
    file.close()
    data = {
        "provisioning_template": {
            "name": template_name,
            "location_ids": location_ids,
            "organization_ids": organization_ids,
            "template": f
        },
        "options": {
            "associate": "always",
        },
    }
    data = json.dumps(data)
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth(config.FOREMAN_USER, config.FOREMAN_PASSWORD)
    r = requests.post(url=url, verify=config.VEREFY,
                      headers=headers, data=data, auth=auth)
    if r.status_code >= 200 and r.status_code <= 299:
        logger.info('import_template - %s' % template_name)
    else:
        logger.error(r.text)


def update_operatingsystems(id_os=1, id_media=[], provisioning_template_ids=[], ptable_ids=[], architecture_ids=[]):
    uri = '/api/operatingsystems'
    url = 'https://%s%s/%s' % (config.FOREMAN_HOST, uri, id_os)
    data = {
        "operatingsystem": {
            "medium_ids": id_media,
            "provisioning_template_ids": provisioning_template_ids,
            "password_hash": "SHA512",
            "ptable_ids": ptable_ids,
            "os_parameters_attributes": [{"name": "username_to_create", "value": "admin"}],
            "architecture_ids": architecture_ids,
        }
    }
    data = json.dumps(data)
    # logger.info(data)
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth(config.FOREMAN_USER, config.FOREMAN_PASSWORD)
    r = requests.put(url=url, verify=config.VEREFY,
                     headers=headers, data=data, auth=auth)
    if r.status_code >= 200 and r.status_code <= 299:
        logger.info('update operatingsystems - %s' % id_os)
    else:
        logger.error(r.text)


def update_operatingsystems_template(id_os=1, os_default_template=[]):
    uri = '/api/operatingsystems/%s/os_default_templates' % id_os
    url = 'https://%s%s' % (config.FOREMAN_HOST, uri)
    data = {
        "os_default_template": os_default_template
    }
    data = json.dumps(data)
    # logger.info(data)
    headers = {'content-type': 'application/json'}
    auth = HTTPBasicAuth(config.FOREMAN_USER, config.FOREMAN_PASSWORD)
    r = requests.post(url=url, verify=config.VEREFY,
                      headers=headers, data=data, auth=auth)
    if r.status_code >= 200 and r.status_code <= 299:
        logger.info('update operatingsystems template - %s' % id_os)
    else:
        logger.error(r.text)


def check_create_subnets(proxy_id, network, network_type, netmask, gateway, domain_ids, location_ids=[2], organization_ids=[1], dns_primary='8.8.8.8', dns_secondary='1.1.1.1'):
    global SESSION
    uri = '/api/subnets'
    uri_search = '%s?search=%s-%s' % (uri, network, network_type)
    url = 'https://%s%s' % (config.FOREMAN_HOST, uri_search)
    headers = {"Cookie": "timezone=Europe%sMoscow; _session_id=%s" %
               ('%2F', SESSION)}
    res = requests.get(url=url, verify=config.VEREFY, headers=headers).json()
    if len(res['results']) == 1:
        logger.info('not need create subnets - %s-%s' %
                    (network, network_type))
    elif len(res['results']) == 0:
        url = 'https://%s%s' % (config.FOREMAN_HOST, uri)
        interface = ipaddress.ip_network(network)
        if network_type == 'os':
            data = {
                "subnet": {
                    "name": "%s-%s" % (network, network_type),
                    "network_type": "IPv4",
                    "network": str(interface.network_address),
                    "mask": netmask,
                    "gateway": gateway,
                    "dns_primary": dns_primary,
                    "dns_secondary": dns_secondary,
                    "boot_mode": "Static",
                    "domain_ids": domain_ids,
                    "location_ids": location_ids,
                    "dhcp_id": proxy_id,
                    "tftp_id": proxy_id,
                    "httpboot_id": proxy_id,
                    "template_id": proxy_id,
                    # "discovery_id":proxy_id,
                    "organization_ids": organization_ids

                }
            }
        elif network_type == 'pxe':
            data = {
                "subnet": {
                    "name": "%s-%s" % (network, network_type),
                    "network_type": "IPv4",
                    "network": str(interface.network_address),
                    "mask": netmask,
                    "gateway": gateway,
                    "dns_primary": dns_primary,
                    "dns_secondary": dns_secondary,
                    "boot_mode": "DHCP",
                    "domain_ids": domain_ids,
                    "location_ids": location_ids,
                    "dhcp_id": proxy_id,
                    "tftp_id": proxy_id,
                    "httpboot_id": proxy_id,
                    "template_id": proxy_id,
                    # "discovery_id":proxy_id,
                    "remote_execution_proxy_ids": proxy_id,
                    "organization_ids": organization_ids,
                    "ipam": 'DHCP',
                    "from": str(interface.broadcast_address-100),
                    "to": str(interface.broadcast_address-1),
                }
            }
        data = json.dumps(data)
        headers = {'content-type': 'application/json'}
        auth = HTTPBasicAuth(config.FOREMAN_USER, config.FOREMAN_PASSWORD)
        r = requests.post(url=url, verify=config.VEREFY,
                          headers=headers, data=data, auth=auth)
        if r.status_code >= 200 and r.status_code <= 299:
            logger.info('create subnet - %s-%s' % (network, network_type))
        else:
            logger.error(r.text)
