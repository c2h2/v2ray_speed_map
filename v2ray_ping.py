from v2ray_speed_map import *
import sys

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


if __name__ == "__main__":
    #check if argv empty
    if len(sys.argv) == 1:
        print("Please enter the airport url")
        sys.exit()
    
    airport_url = sys.argv[1]

    contents = get_sub_links([airport_url])

    airports = parse_sub_links(contents) 
    print(airports)
    airport_dicts = airports_to_dicts(airports)

    kill_v2ray_processes_with_args_containing("v2ray_config_")

    write_airports_to_file(airport_dicts, temp_files_prefix)

    establish_v2ray_connetions(airport_dicts)

    tcp_pings = test_tcp_pings(airport_dicts)

    print("Testing public ip...")
    public_ips=test_public_ip(airport_dicts)

    #test google pings
    print("Testing google pings...")
    google_pings = test_google_pings(airport_dicts)