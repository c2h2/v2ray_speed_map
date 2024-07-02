from v2ray_speed_map import *
from pprint import *

fn_pattern = "test_v2ray_config_9888"
fn = f"/tmp/{fn_pattern}.json"
v2ray_bins = ["./v2ray" , "/opt/v2ray/v2ray"]

    
def establish_v2ray_connection_by_file(fn):
    cmd = f"{v2ray_bin} run -c {fn}"
    if not os.path.exists(fn):
        print(f"file {fn} does not exist, skipping.")
    else:
        logging.info(cmd)
    proc = subprocess.Popen(cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL)
    time.sleep(0.1)
    return proc

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please enter the airport url")
        sys.exit(2)
    
    b64_aiport = sys.argv[1]

    v2ray_bin = ""
    for bin_path in v2ray_bins:
        if os.path.isfile(bin_path) and os.access(bin_path, os.X_OK):
            v2ray_bin = bin_path
            break
    if v2ray_bin == "":
        print("v2ray binary not found, exiting.")
        sys.exit(1)

    
    conf = json.loads(base64.b64decode(b64_aiport).decode('utf-8'))
    conf["inbounds"][0]["port"] = 9888
    json.dump(conf, open(fn, "w"), indent=4)

    kill_v2ray_processes_with_args_containing(fn_pattern) 
    establish_v2ray_connection_by_file(fn)

    value = test_http_ping("http://www.google.com", "localhost", 9888)
    print(value)