import sys
import json
import requests

from links import links
from requests.auth import HTTPBasicAuth
from link_definitions import link_definitions
from dijkstra import Network
from rule_generator import *

hosts = []

for arg in sys.argv:
    hosts.append(arg.lower())

italy_network = Network()
italy_network.load_links_from_dict(links)

flow_rule_json = {}

with open("./flow_rule.json") as file:
    flow_rule_json = json.load(file)

URL = "http://192.168.8.129:8181/onos/v1/"
user = HTTPBasicAuth('onos', 'rocks')
res = requests.get(URL+"links", auth=user)

links = res.json()


path = italy_network.find_path(int(hosts[0]), int(hosts[1]), "thickest")[0]

for i, node_pair in enumerate(path):
    first = i == 0
    last = i == len(path)-1
    if last: i -= 1
    if not (first or last):
        nodes = (path[i-1]+1, path[i]+1, path[i+1]+1)
    else:
        nodes = (path[i]+1, path[i+1]+1)
    print(nodes, hosts)
    if last: new_rule = generate_rule(nodes[::-1], hosts[::-1], links, (first or last))
    else: new_rule = generate_rule(nodes, hosts, links, (first or last))
