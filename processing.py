import requests
import json
import os
import re
from netaddr import IPSet


def proc(event, context):
    p = 0
    sites_list = ['1234', '5678', '2837']
    url = 'https://my.incapsula.com/api/prov/v1/sites/status'
    for k in sites_list:
        params = {'api_id': os.environ['api_id'],
                  'api_key': os.environ['api_key'], 'site_id': k}
        incap = requests.post(url, params=params)
        inputmsg = event['Records'][0]['Sns']['Message']
        webhook_url = inputmsg.split("-")[0]
        ip = inputmsg.split("-")[1]
        print(webhook_url)
        print(ip)
        ipset = IPSet()
        inputset = IPSet()
        incap_response = (json.loads(incap.text)[
                          'security']['acls']['rules'][0])
        ip_json = []
        ip_json.clear()
        for i in incap_response['exceptions']:
            ip_json.append(i['values'][0].get("ips"))
        ip_json = (str(ip_json).replace('\\n', ' '))
        final = re.findall("'(.*?)'", ip_json)
        for j in final:
            if ("-" in j) == False:
                ipset.add(j)
        inputset.add(ip)
        for j in inputset:
            if (j in ipset) == True:
                p = 1
            else:
                p = 0
                break
    print(p)
    if p == 1:
        slack_data = '{"text":"IP is Whitelisted!!"}'
        final_response = requests.post(
            url=webhook_url, data=slack_data,
            headers={'Content-Type': 'application/json'}
        )
    else:
        slack_data = '{"text":"IP is not Whitelisted!!"}'
        final_response = requests.post(
            url=webhook_url, data=slack_data,
            headers={'Content-Type': 'application/json'}
        )
        print(final_response)
