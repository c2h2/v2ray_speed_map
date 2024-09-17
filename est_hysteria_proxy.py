import json
import requests
import base64
import os
import sys
import urllib.parse
import yaml
import time
def read_config():
    with open("config.json", "r") as f: 
        configs = json.load(f)
    return configs

def get_sub_links(urls):
    contents = []
    for url in urls:
       r = requests.get(url)
       contents.append(r.text)
    return contents

def parse_sub_links(sub_links):
    ret = []
    idx = 0
    for sub_link in sub_links:
        ret.append([])
        sub = base64.b64decode(sub_link).decode("utf-8")
        sub_lines = sub.split("\n")
        for sub_line in sub_lines:
            if "hysteria" in sub_line:
                ret[idx].append(sub_line)
        idx += 1
    return ret

# Generate the JSON configuration
def generate_hysteria_configs(hysteria_links, conf_hysteria):
    idx=0
    h_links = [item for sublist in hysteria_links for item in sublist]
    for h in h_links:
        comments = h.split("#")[-1]
        
        decoded_comments = urllib.parse.unquote(comments)
        print(decoded_comments)
        print(idx, h)
        conf = hysteria_link_to_yaml(h, 0)
        with open(f"/opt/hysteria_{idx}.yaml", "w") as f:
            f.write(conf)
        idx += 1



def hysteria_link_to_yaml(link, offset):
    socks_port = 10810
    http_port = 11810
    parsed_link = urllib.parse.urlparse(link)
    auth = parsed_link.username
    hostname = parsed_link.hostname
    port = parsed_link.port
    query_params = urllib.parse.parse_qs(parsed_link.query)
    comments = parsed_link.fragment
    # Handle multiple ports (mport) if present
    if 'mport' in query_params:
        mport = query_params['mport'][0]
        server = f"{hostname}:{mport}"
    else:
        server = f"{hostname}:{port}"
    
    # Extract TLS parameters
    tls = {}
    tls['insecure'] = query_params.get('insecure', ['0'])[0] == '1'
    tls['sni'] = query_params.get('sni', [''])[0]
    
    # Build the configuration dictionary
    config = {
        'server': server,
        'auth': auth,
        'tls': tls,
        'transport': {
            'type': 'udp',
            'udp': {
                'hopInterval': '30s'
            }
        },
        'quic': {
            'initStreamReceiveWindow': 8388608,
            'maxStreamReceiveWindow': 8388608,
            'initConnReceiveWindow': 20971520,
            'maxConnReceiveWindow': 20971520,
            'maxIdleTimeout': '30s',
            'keepAlivePeriod': '10s',
            'disablePathMTUDiscovery': True
        },
        'fastOpen': True,
        'lazy': True,
        'socks5': {
            'listen': f'127.0.0.1:{socks_port + offset}'
        },
        'http': {
            'listen': f'127.0.0.1:{http_port + offset}'
        },
        'comments': comments,
    }
    
    # Convert the configuration dictionary to YAML
    yaml_config = yaml.dump(config, sort_keys=False, default_flow_style=False, allow_unicode=True)
    
    return yaml_config







if __name__ == "__main__":
    configs = read_config()
    template_hysteria = configs["template_hysteria"]
    conf_hysteria = open(template_hysteria, "r").read()
    sub_links = get_sub_links(configs["sub_urls"])
    hysteria_links = parse_sub_links(sub_links)
    generate_hysteria_configs(hysteria_links, conf_hysteria)
