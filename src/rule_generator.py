import json
import requests

from requests.auth import HTTPBasicAuth
URL = "http://192.168.33.5:8181/onos/v1/"
user = HTTPBasicAuth('karaf', 'karaf')

def convert_to_id(n):
    n = int(n)
    return "of:"+(f"{n:x}".zfill(16))

def generate_rule(switches, hosts, links, edge=True):
    switch_ids = []
    for switch in switches:
        switch_ids.append(convert_to_id(switch))

    if edge:
        current_link = {}
        for link in links["links"]:
            link_tuple = (link["src"]["device"], link["dst"]["device"])
            if sorted(link_tuple) == sorted(switch_ids):
                current_link = {link["src"]["device"]: link["src"]["port"], link["dst"]["device"]: link["dst"]["port"]}
                break

        port_numbers = [current_link.get(switch_ids[0]),
                        current_link.get(switch_ids[1])]
        port_numbers[1] = "1"
        edited_switch = switch_ids[0]

    else:
        current_link = []
        for link in links["links"]:
            link_tuple = (link["src"]["device"], link["dst"]["device"])
            if sorted(link_tuple) == sorted(switch_ids[0:2]):
                current_link.append({link["src"]["device"]: link["src"]["port"], link["dst"]["device"]: link["dst"]["port"]})
                break

        for link in links["links"]:
            link_tuple = (link["src"]["device"], link["dst"]["device"])
            if sorted(link_tuple) == sorted(switch_ids[1:3]):
                current_link.append({link["src"]["device"]: link["src"]["port"], link["dst"]["device"]: link["dst"]["port"]})
                break
        
        print(current_link)
        port_numbers = [current_link[1].get(switch_ids[1]),
                        current_link[0].get(switch_ids[1])]
        edited_switch = switch_ids[1]

    # loading json template from file
    flow_rule_json = {}

    with open("./flow_rule.json") as file:
        flow_rule_json = json.load(file)

    # modifying flow rules for each of switches
    n = 1
    switch_rule = flow_rule_json
    switch_rule["deviceId"] = edited_switch

    switch_rule["treatment"]["instructions"][0]["port"] = port_numbers[1]
    switch_rule["selector"]["criteria"][0]["port"] = port_numbers[0]
    switch_rule["selector"]["criteria"][2]["ip"] = f"10.0.0.{hosts[0][1:]}/32"
    res = requests.post(URL + "flows/" + edited_switch, data=json.dumps(switch_rule), auth=user)
    

    with open("./new_rule.json", "a") as out_file:
        json.dump(switch_rule, out_file, indent=2)
    n+=1
    switch_rule["treatment"]["instructions"][0]["port"] = port_numbers[0]
    switch_rule["selector"]["criteria"][0]["port"] = port_numbers[1]
    switch_rule["selector"]["criteria"][2]["ip"] = f"10.0.0.{hosts[1][1:]}/32"
    res = requests.post(URL + "flows/" + edited_switch, data=json.dumps(switch_rule), auth=user)
    
    n+=1

    with open("./new_rule.json", "a") as out_file:
        json.dump(switch_rule, out_file, indent=2)
