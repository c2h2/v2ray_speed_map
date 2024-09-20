import json
import requests
import base64
import os
import sys
import urllib.parse
import yaml
import time
import socket
import subprocess
import socks  # You need to install PySocks
import signal
import random
import yaml

def read_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return None

def find_config_files(directory):
    """
    Finds all files matching the pattern hysteria_*.yaml in the specified directory.
    Returns a list of matching file paths.
    """
    config_files = []
    for filename in os.listdir(directory):
        if filename.startswith('hysteria_') and filename.endswith('.yaml'):
            config_files.append(os.path.join(directory, filename))
    return config_files

def start_hysteria_client(config_file):
    """
    Starts the hysteria client with the specified configuration file.
    Returns the subprocess.Popen object representing the client process.
    """
    hysteria_executable = '/opt/bin/hysteria'
    command = [hysteria_executable, '-c', config_file]
    process = subprocess.Popen(command)
    print(f"Started hysteria client with config: {config_file}")
    decoded_comments = urllib.parse.unquote(read_yaml(config_file)["comments"])
    print(decoded_comments)

    return process

def test_connection_via_socks(proxy_host='localhost', proxy_port=10810, test_host='google.com', test_port=80, timeout=10):
    """
    Tests if a connection to test_host:test_port can be made via the SOCKS proxy.
    Returns True if the connection is successful, False otherwise.
    """
    try:
        # Set up a SOCKS5 proxy
        socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
        socket.socket = socks.socksocket

        # Attempt to connect to the test host and port
        with socket.create_connection((test_host, test_port), timeout=timeout):
            print(f"Successfully connected to {test_host}:{test_port} via SOCKS proxy at {proxy_host}:{proxy_port}.")
            return True
    except Exception as e:
        print(f"Failed to connect to {test_host}:{test_port} via SOCKS proxy at {proxy_host}:{proxy_port}: {e}")
        return False
    finally:
        # Reset the socket module to its default state
        socks.set_default_proxy()
        socket.socket = socket._socketobject if hasattr(socket, "_socketobject") else socket.SocketType


def test_http_ping(url, socks_host, socks_port, timeout=5, times=0):
    if times >= 3:
        return 9999
    try:
        start_time = time.time()
        proxies = {'http': f"socks5h://{socks_host}:{socks_port}", 'https': f"socks5h://{socks_host}:{socks_port}"}
        resp = requests.get(url, proxies=proxies, timeout=timeout)
        if(resp.status_code == 200 or resp.status_code==302):
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        else:
            return test_http_ping(url, socks_host, socks_port, timeout=timeout, times=times+1)
        return round(duration_ms, 0)  # Return duration in ms, rounded to 1 decimal place
    except Exception as e:
        return test_http_ping(url, socks_host, socks_port, timeout=timeout, times=times+1)

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

def generate_hysteria_configs(hysteria_links, conf_hysteria):
    idx=0
    h_links = [item for sublist in hysteria_links for item in sublist]
    subprocess.run("rm /opt/hysteria_*.yaml", shell=True)
    
    for h in h_links:
        comments = h.split("#")[-1]
        decoded_comments = urllib.parse.unquote(comments)
        if ("美国" in decoded_comments):
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



def main():
    directory = "/opt"
    socks_proxy_port = 10810
    check_interval = 30
    configs = read_config()
    sub_links = get_sub_links(configs["sub_urls"])
    hysteria_links = parse_sub_links(sub_links)
    generate_hysteria_configs(hysteria_links, conf_hysteria)


    config_files = find_config_files(directory)
    if not config_files:
        print("No configuration files found matching the pattern hysteria_*.yaml.")
        sys.exit(1)

    print(f"Found {len(config_files)} configuration files.")

    current_process = None
    switch_cnt = 0
    try:
        while True:
            # Select a random configuration file
            config_file = random.choice(config_files)

            # Start the hysteria client
            current_process = start_hysteria_client(config_file)

            # Wait for a short period to allow the client to start
            time.sleep(2)

            # Periodically check if the connection via SOCKS proxy is working
            while True:

                elapsed_time = test_http_ping("http://google.com", "localhost", 10810)
                if elapsed_time < 4000:
                    server_name = urllib.parse.unquote(read_yaml(config_file)["comments"])
                    print(server_name)
                    print(f"Google ping: {elapsed_time} ms. config file is: {config_file}, switched {switch_cnt} times." )
                    time.sleep(check_interval)
                else:
                    switch_cnt += 1 
                    print("Connection via SOCKS proxy failed. Restarting the hysteria client.")
                    # Terminate the current process
                    current_process.terminate()
                    try:
                        current_process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        current_process.kill()
                    break  # Break the inner loop to select a new config and restart
    except KeyboardInterrupt:
        print("Script interrupted by user.")
    finally:
        # Clean up: Terminate the hysteria client if it's running
        if current_process and current_process.poll() is None:
            print("Terminating hysteria client.")
            current_process.terminate()
            try:
                current_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                current_process.kill()
        print("Script exited.")
        



if __name__ == "__main__":
    main()
    #now maintian socks proxy

