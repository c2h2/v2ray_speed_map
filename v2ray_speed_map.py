#download a page
import requests
import json
import base64 

def get_sub_links(urls):
    contents = []
    for url in urls:
       r = requests.get(url)
       contents.append(r.text)
    return contents

def parse_sub_links(contents):
    #load base64
    airports=[]
    for b64 in contents:
        #decode base64
        nodes_text = base64.b64decode(str.encode(b64) + b'=' * (-len(b64) % 4))
        nodes = nodes_text.decode().strip().split('\n')
        if len(nodes) < 10 or nodes == None:
            continue
        for node in nodes:
            if len(node) < 10 or node == None:
                continue
            try:
                scheme = node.split('://')[0]
                node_b64 = node.split('://')[1]
                if scheme == 'vmess':
                    airport={}
                    airport["scheme"] = scheme
                    vmess_config = json.loads(base64.b64decode(node_b64).decode("utf-8"))
                    airport["org_str"] = node
                    #merge vmess_config to airport
                    airport.update(vmess_config)
                    airports.append(airport)
            except Exception as e:
                print(node)
                print(e)
    return airports



if __name__ == '__main__':
    with open("config.json", "r") as f:
        config = json.load(f)
    contents = get_sub_links(config["urls"])
    airports = parse_sub_links(contents)

    for airport in airports:
        pass
        #print(airport)
