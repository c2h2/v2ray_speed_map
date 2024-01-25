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
from subprocess import DEVNULL, STDOUT, check_call
import socks
import os
import sys


#globals
configs=[]
save_all_server_configs = True
create_relay_configs = True
all_server_configs_dir = "/tmp"
socks_start_port=1100
just_build_configs=True


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

def build_config_by_airport(airport):
    config_template=json.load(open(configs["template_vmess_client"],"r"))
    if airport["scheme"] == "vmess":     
        new_config = config_template.copy()
        comments = airport["ps"]
        new_config["outbounds"][0]["settings"]["vnext"][0]["address"] = airport["add"]
        new_config["outbounds"][0]["settings"]["vnext"][0]["port"] = int(airport["port"])
        new_config["outbounds"][0]["settings"]["vnext"][0]["users"][0]["id"] = airport["id"]
        new_config["outbounds"][0]["settings"]["vnext"][0]["users"][0]["alterId"] = int(airport["aid"])
        new_config["comments"] = comments
        return new_config, comments
    return None, None

def build_dicts_by_airports(airports):
    
    for airport in airports:
        new_config, comment = build_config_by_airport(airport)
        if new_config != None:
            airport.update(new_config)
            airport["comments"] = comment

    new_configs = []
    for airport in airports:
        new_config, comment = build_config_by_airport(airport)
        new_config["comments"] = comment
        new_configs.append(new_config.copy())
    return new_configs

def get_relay_config_fn_by_id(id):
    return f"{all_server_configs_dir}/v2ray_relay_config_{id}.json"

def get_client_config_fn_by_id(id):
    return f"{all_server_configs_dir}/v2ray_config_{id}.json"

def build_client_json_configs(airport_dicts):
    for idx, airport in enumerate(airport_dicts):
        l_airport = airport.copy()
        l_airport["inbounds"][0]["port"] = socks_start_port + idx
        with open(get_client_config_fn_by_id(idx), "w") as f:
            json.dump(l_airport, f, indent=2)

def build_relay_json_configs(airport_dicts):
    airport_relay = json.load(open(configs["template_relay"],"r"))
    for idx, airport in enumerate(airport_dicts):
        airport_relay["outbounds"] = airport["outbounds"].copy()
        with open(get_relay_config_fn_by_id(idx), "w") as f:
            json.dump(airport_relay, f, indent=2)

def test_http_ping(url, socks_host, socks_port, timeout=6, times=0):
    if times >= 3:
        return 9999
    try:
        start_time = time.time()
        proxies = {'http': f"socks5h://{socks_host}:{socks_port}", 'https': f"socks5h://{socks_host}:{socks_port}"}
        resp = requests.get(url, proxies=proxies, timeout=timeout)
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        return round(duration_ms, 1)  # Return duration in ms, rounded to 1 decimal place
    except Exception as e:
        return test_http_ping(url, socks_host, socks_port, timeout=timeout, times=times+1)

def test_tcp_ping(airport, timeout=5):
    try:
        host = airport["outbounds"][0]["settings"]["vnext"][0]["address"]
        port = int(airport["outbounds"][0]["settings"]["vnext"][0]["port"])
    except:
        return -2
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

def speedtest_download_file2(socks_host, socks_port):
    timeout = 20
    url = configs["test_url"]
    socks.set_default_proxy(socks.SOCKS5, socks_host, socks_port)  # Change to your SOCKS proxy settings
    socket.socket = socks.socksocket

    start_time = time.time()
    bytes_downloaded = 0
    try:
        with requests.get(url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk:
                    bytes_downloaded += len(chunk)
                    current_time = time.time()
                    if current_time - start_time > timeout:
                        break
        elapsed_time = time.time() - start_time
        speed_bps = bytes_downloaded / elapsed_time
        speed_kbps = speed_bps / 1024
        speed_mbps = speed_kbps / 1024
        return round(speed_mbps*8,2)
    except requests.Timeout:
        # Calculate speed based on data downloaded so far
        elapsed_time = time.time() - start_time
        speed_bps = bytes_downloaded / elapsed_time
        speed_kbps = speed_bps / 1024
        speed_mbps = speed_kbps / 1024
        return round(speed_mbps*8,2)
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return -1

def speedtest_download_file(socks_host, socks_port):
    url = configs["test_url"]
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
            speed_mbps = speed_bps / (1024 * 1024) * 8 # Convert to Megabits per second
            speed_mbps = round(speed_mbps, 1)
            return speed_mbps
        except Exception as e:
            return -1

def test_tcp_pings(airport_dicts):
    tcp_pings = []
    for idx, airport in enumerate(airport_dicts):
        ping = test_tcp_ping(airport)
        tcp_pings.append(ping)
        try:
            print(f"{idx} {airport_dicts[idx]['comments']} {ping} ms.")
        except: #not an airport
            pass
    
    return tcp_pings

def test_google_pings(airport_dicts):
    google_pings = []
    for idx, airport in enumerate(airport_dicts):
        socks_host = "localhost"
        socks_port = airport["inbounds"][0]["port"]
        print(f"Testing {socks_host}:{socks_port} -> google.com")
        res = test_http_ping("http://google.com", socks_host, socks_port)
        print(f"{idx} {airport['comments']} -> google.com = {res} ms")
        google_pings.append(res)
    return google_pings

def test_speeds(airport_dicts):
    speeds = []
    for idx, airport in enumerate(airport_dicts):
        try:
            res = speedtest_download_file2("localhost", airport["inbounds"][0]["port"])
        except:
            res = -1
        speeds.append(res)
        scheme = airport["outbounds"][0]["protocol"]
        address = airport["outbounds"][0]["settings"]["vnext"][0]["address"]
        print(f"{idx} {airport['comments']} -> {scheme} {address} = {res} Mbps")
    return speeds

def create_relay_dict(airport_config, relay_template):#only vmess for now.
    relay_dict=json.load(open(relay_template,"r"))
    relay_dict["outbounds"][0]=airport_config["outbounds"][0].copy()
    return relay_dict

def test_public_ip(airport_dicts):
    ips = []
    for idx, airport in enumerate(airport_dicts):
        socks_host = "localhost"
        socks_port = airport["inbounds"][0]["port"]
        proxies = {'http': f"socks5h://{socks_host}:{socks_port}", 'https': f"socks5h://{socks_host}:{socks_port}"}
        try:
            res = requests.get("http://ifconfig.me", proxies=proxies, timeout=5).text
            print(f"{idx} {airport['comments']} -> IP = {res}")
        except:
            res = "FAILED"
        ips.append(res)
    return ips

def usage():
    print("usage: python3 v2ray_speed_map.py")
    print("example configs need to be copid to jsons and in the same directory as this script.")

def establish_v2ray_connetions(airport_dicts):
    procs=[]
    for idx, airport in enumerate(airport_dicts):
        if airport["outbounds"][0]["protocol"] == "vmess":
            cmd = f"v2ray/v2ray run -c {get_client_config_fn_by_id(idx)}"
            print(cmd)
            procs.append(subprocess.Popen(cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL))
    return procs

def kill_v2ray_connetions(procs):
    for proc in procs:
        proc.kill()

#this program read sublinks from config.json, it will produce client configs for speed and ping test, and relay configs, it follows:
#load config
#dl sub links
#parse sub links
#convert links b64 to dict
#convert to v2ray client config json files
#convert to v2ray relay config json files
#test tcp ping
#establish v2ray client link
#test google ping
#test speed
#test ip
#build big 2d table of all results, （airport ps, scheme, host, port, tcp ping, google ping, speed mbps）
#choose optimal relay configs
#build html and js，save results to json dump


if __name__ == '__main__':
    airport_res_dicts = []
    #load config
    with open("config.json", "r") as f: configs = json.load(f)
    #dl sub links   
    print("Downloading sub links...", end="") 
    contents = get_sub_links(configs["sub_urls"]) #become whole base64
    print("done")
    #parse sub links
    airports = parse_sub_links(contents) #become json of each airport, each "airports” is a jsons of a sub link.
    #convert links b64 to dict
    airport_dicts = build_dicts_by_airports(airports)
    #convert to v2ray client config json files
    build_client_json_configs(airport_dicts)
    #convert to v2ray relay config json files
    build_relay_json_configs(airport_dicts)

    if just_build_configs:
        sys.exit(0)
    #establish v2ray client link
    establish_v2ray_connetions(airport_dicts)
    #test tcp pings
    print("Testing tcp pings...")
    tcp_pings = test_tcp_pings(airport_dicts)
    print("done tcp pings")
    #test public ip
    print("Testing public ip...")
    public_ips=test_public_ip(airport_dicts)
    #test google pings
    print("Testing google pings...")
    google_pings = test_google_pings(airport_dicts)
    print("done google pings")
    #test speeds
    print("Testing dl speeds...")
    speed_mbps = test_speeds(airport_dicts)
    print("done")

    #build big 2d table of all results, （airport ps, scheme, host, port, tcp ping, google ping, speed mbps）
    for idx, airport in enumerate(airport_dicts):
        airport_res_dicts.append({})
        airport_res_dicts[-1]["comments"] = airport["comments"]
        airport_res_dicts[-1]["airport"] = airport.copy()
        airport_res_dicts[-1]["tcp_ping"] = tcp_pings[idx]
        airport_res_dicts[-1]["google_ping"] = google_pings[idx]
        airport_res_dicts[-1]["speed_mbps"] = speed_mbps[idx]
        airport_res_dicts[-1]["ip"] = public_ips[idx]

    #save results to json dump, file name is YYYY-MM-DD-HH-MM-SS_v2ray_results.json, path is results/ relative to this script.
    if not os.path.exists("results"):
        os.makedirs("results")
    with open(f"results/{time.strftime('%Y-%m-%d-%H-%M-%S')}_v2ray_results.json", "w") as f:
        json.dump(airport_res_dicts, f, indent=2)
       

    #choose optimal relay configs
    

    #export relay b64 sub links
    
    #build html and js
        
    