#download a page
import requests
import json
import base64 

#test pings
import socket
import time

#parse trojan
from urllib.parse import urlparse, unquote


#globals
all_airports = []
all_airports_extra = []

def get_sub_links(urls):
    contents = []
    for url in urls:
       r = requests.get(url)
       contents.append(r.text)
    return contents

def parse_trojan(trojan_url):
    # Parse the URL
    parsed_url = urlparse(trojan_url)

    # Extract the token (username)
    token = parsed_url.username

    # Extract the host and port
    host = parsed_url.hostname
    port = parsed_url.port

    # Parse the query parameters
    query_params = parsed_url.query

    # Decode the fragment
    description = unquote(parsed_url.fragment)

    # Output the parsed information
    parsed_info = {
        "token": token,
        "host": host,
        "port": port,
        "query_params": query_params,
        "description": description
    }

    return parsed_info

def parse_sub_links(contents):
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
                
                airport={}
                airport["scheme"] = scheme
                if scheme == 'trojan':
                    trojan_config = parse_trojan(node)
                    airport["add"] = trojan_config["host"]
                    airport["port"] = trojan_config["port"]
                    airport["ps"] = trojan_config["description"]
                    airport["id"] = trojan_config["token"]
                if scheme == 'vmess':
                    vmess_config = json.loads(base64.b64decode(node_b64).decode("utf-8"))
                    #merge vmess_config to airport
                    airport.update(vmess_config)
                if scheme == 'vless':
                    vless_config = json.loads(base64.b64decode(node_b64).decode("utf-8"))
                    airport.update(vless_config)
                if scheme == 'ss' or scheme == 'ssr':
                    ss_config = base64.b64decode(node_b64).decode("utf-8")
                    airport["add"] = ss_config.split("@")[1].split(":")[0]
                    airport["port"] = ss_config.split("@")[1].split(":")[1]
                    airport["ps"] = ss_config.split("@")[0]
                    airport["id"] = ss_config.split("@")[0]
                    airport["aid"] = 0
                    airport["net"] = "shadowsocks"
                    airport["type"] = "none"
                    airport["host"] = ""
                    airport["path"] = ""
                    airport["tls"] = ""
                    airport["sni"] = ""

                
                    
                airport["org_str"] = node
                
                airports.append(airport)
            except Exception as e:
                print(node)
                print(e)
    return airports

def build_config_by_airport(airport, config_template):
    if airport["scheme"] == "vmess":     
        new_config = config_template
        comments = airport["ps"]
        new_config["outbounds"][0]["settings"]["vnext"][0]["address"] = airport["add"]
        new_config["outbounds"][0]["settings"]["vnext"][0]["port"] = int(airport["port"])
        new_config["outbounds"][0]["settings"]["vnext"][0]["users"][0]["id"] = airport["id"]
        new_config["outbounds"][0]["settings"]["vnext"][0]["users"][0]["alterId"] = int(airport["aid"])
        #json.dump(new_config, open(f"/tmp/v2ray_config{len(all_airports)}.json","w"), indent=2)
        #json.dump(new_config, open(f"/tmp/v2ray_config{len(all_airports)}.json","w"), indent=2)
        new_config["comments"] = comments
        return new_config, comments
    return None, None

def test_tcp_ping(airport, timeout=5):
    host = airport["add"]
    port = int(airport["port"])
    message = "hello"

    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))

            # Send the message
            start_time = time.time()
            s.sendall(message.encode())

            # Wait for a response
            response = s.recv(1024)
            end_time = time.time()

            # Calculate round-trip time
            duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            return round(duration_ms, 1)  # Return duration in ms, rounded to 1 decimal place
    except socket.timeout:
        return 9999
    except Exception as e:
        return f"Failed: {e}"
    

if __name__ == '__main__':
    config_template = json.load(open("template_vmess.json","r"))
    with open("config.json", "r") as f:
        config = json.load(f)
    contents = get_sub_links(config["urls"]) #become whole base64
    airports = parse_sub_links(contents) #become json of each airport, each "airports” is a jsons of a sub link.

    # build configs for each airport
    if airports != None:    
        for idx, airport in enumerate(airports):
            airport_config, comments = build_config_by_airport(airport, config_template)
            all_airports.append(airport_config) #become a list of jsons of each airport
            all_airports_extra.append(comments)
            # test tcp ping for each airport    
            res = test_tcp_ping(airport)
            ps = airport["ps"]
            host = airport["add"]
            scheme = airport["scheme"]
            print(f"{idx} {ps} -> {scheme} {host} = {res}ms")
            
