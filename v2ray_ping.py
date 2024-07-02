from v2ray_speed_map import *
import sys
import datetime
import requests

temp_files_prefix = "/tmp/v2ray_config_"

def get_v2ray_ping(airport_url):
    # Get the v2ray server list
    v2ray_server_list = get_v2ray_server_list(airport_url)
    print("v2ray_server_list: ", v2ray_server_list)

    # Get the v2ray server ping
    v2ray_server_ping = get_v2ray_server_ping(v2ray_server_list)
    print("v2ray_server_ping: ", v2ray_server_ping)

    return v2ray_server_ping

def write_airports_to_file(airport_dicts, temp_files_prefix):
    for i, airport_dict in enumerate(airport_dicts):
        with open(temp_files_prefix + str(i) +".json", 'w') as f:
            f.write(json.dumps(airport_dict))

def report_pings_to_server(url, results_json):
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(results_json), headers=headers)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

if __name__ == "__main__":
    #check if argv empty
    if len(sys.argv) == 1:
        print("Please enter the airport url")
        sys.exit()

    airport_urls = sys.argv[1:]

    direct_ping = direct_ping()
    direct_ip = direct_ip()

    print("Testing direct pings: ", direct_ping, "ms. ip: ", direct_ip)

    contents = get_sub_links(airport_urls)

    airports = parse_sub_links(contents) 

    airport_dicts = airports_to_dicts(airports)

    airport_names = [airport_dict["comments"] for airport_dict in airport_dicts]
  
    kill_v2ray_processes_with_args_containing("v2ray_config_")

    write_airports_to_file(airport_dicts, temp_files_prefix)

    establish_v2ray_connetions(airport_dicts)

    tcp_pings = test_tcp_pings(airport_dicts)

    print(tcp_pings)

    print("Testing public ip...")
    public_ips=test_public_ip(airport_dicts)

    print(public_ips)

    #test google pings
    print("Testing google pings...")
    google_pings = test_google_pings(airport_dicts)

    print(google_pings)
    hostname = socket.gethostname()
    results = []
    for i, airport_names in enumerate(airport_names):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        results.append({"initiator": hostname,"data_type":"remote_test", "name": airport_names, "tcp_ping": tcp_pings[i], "google_ping": google_pings[i], "public_ip": public_ips[i], "created_at": ts})
    results.append({"initiator": hostname,"data_type":"remote_test", "name": "direct", "tcp_ping": 0, "google_ping": direct_ping, "public_ip": direct_ip, "created_at": ts})
    
    print(results)

    report_pings_to_server(configs["post_remote_server_url"], results)
    