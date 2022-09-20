#!/usr/bin/env python

from ansible.module_utils.basic import *
import requests
import json

try:
    from akamai.edgegrid import EdgeGridAuth, EdgeRc
except ImportError:
    print("Please install `edgegrid-python` using pip")
from os.path import expanduser
from urlparse import urljoin

DOCUMENTATION = ''' docs '''
EXAMPLES = ''' examples '''

def get_request_file(json_file):
    with open(json_file, "r") as j:
        body = json.load(j)

    return body

def authenticate(params):
    # get home location
    home = expanduser("~")
    filename = "%s/.edgerc" % home

    # extract edgerc properties
    edgerc = EdgeRc(filename)

    # values from ansible
    endpoint = params["endpoint"]
    section = params["section"]

    # creates baseurl for akamai
    baseurl = 'https://%s' % edgerc.get(section, 'host')

    s = requests.Session()
    s.auth = EdgeGridAuth.from_edgerc(edgerc, section)

    if params["method"] == "GET":
        response = s.get(urljoin(baseurl, endpoint))
        if response.status_code != 400 and response.status_code != 404:
            return False, False, response.json()
        else:
            return True, False, response.json()
    elif params["method"] == "POST":
        body = get_request_file(params["body"])
        headers = {'content-type': 'application/json'}
        response = s.post(urljoin(baseurl, endpoint), json=body, headers=headers)
        if response.status_code != 400 and response.status_code != 404:
            return False, True, response.json()
        else:
            return True, False, response.json()
    elif params["method"] == "PUT":
        body = get_request_file(params["body"])
        headers = {'content-type': 'application/json'}
        response = s.put(urljoin(baseurl, endpoint), json=body, headers=headers)
        if response.status_code != 400 and response.status_code != 404:
            return False, True, response.json()
        else:
            return True, False, response.json()
    else:  # error
        pass


def main():
    fields = {
        "section": {"required": True, "type": "str"},
        "endpoint": {"required": True, "type": "str"},
        "method": {"required": True, "type": "str"},
        "body": {"required": False, "type": "str"},
        "headers": {"required": False, "type": "str"}
    }

    module = AnsibleModule(argument_spec=fields)

    is_error, has_changed, result = authenticate(module.params)

    if not is_error:
        module.exit_json(changed=has_changed, msg=result)
    else:
        module.fail_json(msg=result)

if __name__ == "__main__":
    main()
