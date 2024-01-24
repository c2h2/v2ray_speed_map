#download a page
import requests
import json
import base64 

#test pings
import socket
import time

#parse trojan
from urllib.parse import urlparse, unquote

import subprocess
import socks

#globals
test_url = 'http://ipv4.download.thinkbroadband.com/100MB.zip' #replace with your own url in config.json
all_airport_dict_configs = [] #become a list of jsons of each airport
all_airports_extra = [] #become a list of comments/ps of each airport
all_airports_tcp_pings = [] #become a list of pings of each airport
all_airports_google_pings = [] #become a list of site pings of each airport
all_airports_dl_speeds = [] #become a list of download speeds of each airport

tmp_v2ray_config = "/tmp/v2_config.json"
save_all_server_configs = True
all_server_configs_dir = "/tmp"
create_relay_configs = True

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
        new_config["comments"] = comments
        return new_config, comments
    return None, None

def test_http_ping(url, timeout=6, times=0):
    if times >= 3:
        return 9999
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        return round(duration_ms, 1)  # Return duration in ms, rounded to 1 decimal place
    except Exception as e:
        return test_http_ping(url, timeout=timeout, times=times+1)

def test_tcp_ping(airport, timeout=5):
    host = airport["add"]
    port = int(airport["port"])
    dummy_message = "hello"

    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))

            start_time = time.time()
            s.sendall(dummy_message.encode())

            response = s.recv(1024)
            end_time = time.time()
            
            duration_ms = (end_time - start_time) * 1000 # Calculate round-trip time
            return round(duration_ms, 1)  # Return duration in ms, rounded to 1 decimal place
    except socket.timeout:
        return 9999
    except Exception as e:
        return 9999
    
def build_html_and_js():
    #do this later.
    pass

def speedtest_download_file(socks_host, socks_port, url=test_url):
    socks.set_default_proxy(socks.SOCKS5, socks_host, socks_port)  # Change to your SOCKS proxy settings
    socket.socket = socks.socksocket

    start_time = time.time()
    response = requests.get(url, stream=True, timeout=60)
    
    total_length = response.headers.get('content-length')

    if total_length is None:  # no content length header
        print("Couldn't retrieve the file")
    else:
        try:
            total_length = int(total_length)
            bytes_downloaded = 0

            for data in response.iter_content(chunk_size=4096):
                bytes_downloaded += len(data)

            end_time = time.time()
            duration = end_time - start_time
            speed_bps = bytes_downloaded / duration
            speed_mbps = speed_bps / (1024 * 1024)  # Convert to Megabits per second

            print(f"Download speed: {speed_mbps:.2f} Mbps")
            return speed_mbps
        except Exception as e:
            return -1

def create_relay_json(airport_config, relay_template):#only vmess for now.
    relay_dict=json.load(open(relay_template,"r"))
    relay_dict["outbounds"][0]=airport_config["outbounds"][0]
    return json.dumps(relay_dict)
    
    
if __name__ == '__main__':
    config_template = json.load(open("template_vmess.json","r"))
    with open("config.json", "r") as f:
        config = json.load(f)
    contents = get_sub_links(config["sub_urls"]) #become whole base64
    test_url = config["test_url"]
    airports = parse_sub_links(contents) #become json of each airport, each "airports” is a jsons of a sub link.

    # build configs for each airport and
    # test tcp ping for each airport
    if airports != None:    
        for idx, airport in enumerate(airports):
            airport_config, comments = build_config_by_airport(airport, config_template)
            all_airport_dict_configs.append(airport_config) #become a list of jsons of each airport
            all_airports_extra.append(comments)
            # test tcp ping for each airport    
            res = test_tcp_ping(airport)
            ps = airport["ps"]
            host = airport["add"]
            scheme = airport["scheme"]
            all_airports_tcp_pings.append(res)
            print(f"{idx} {ps} -> {scheme} {host} = {res}ms")
            
    #test google ping and speed for each airport
    for idx, airport_config in enumerate(all_airport_dict_configs):
        v2ray_config = airport_config
        comments = all_airports_extra[idx]
        with open(tmp_v2ray_config, "w") as f:
            json.dump(v2ray_config, f, indent=2)
        if save_all_server_configs:
            with open(f"{all_server_configs_dir}/v2ray_config_{idx}.json", "w") as f:
                json.dump(v2ray_config, f, indent=2)
        
        if create_relay_configs:
            j=create_relay_json(airport_config, "relay_config.json")
            with open(f"{all_server_configs_dir}/v2ray_relay_config_{idx}.json", "w") as f:
                json.dump(j, f, indent=2)
    
        #subprocess to run v2ray in background and kill later
        cmd = f"v2ray/v2ray run -c {tmp_v2ray_config}"
        proc = subprocess.Popen(cmd, shell=True)
        #run custom speed test
        time.sleep(2)
        ps = airport_config["comments"]
        host = airport_config["outbounds"][0]["settings"]["vnext"][0]["address"]
        scheme = airport_config["outbounds"][0]["protocol"]
        socks_host = "localhost"
        socks_port = airport_config["inbounds"][0]["port"]
        print(f"{idx} {ps} -> {scheme} {host} testing pings = ", end="", flush=True)
        google_ping = test_http_ping("http://google.com") #dont use ssl handshake stuff. just use http ping
        print(f"{google_ping}ms")
        print(f"{idx} {ps} -> {scheme} {host} testing speed = ", end="", flush=True)
        mbps = round(speedtest_download_file(socks_host, socks_port),3)
        print(f"{mbps}mbps")
        proc.terminate()
        all_airports_google_pings.append(google_ping)
        all_airports_dl_speeds.append(mbps)
    