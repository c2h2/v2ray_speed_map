import requests
import base64
import subprocess
import sys
import json
import os


def update_hosts_file(ips):
    # Sort the IPs by their values (ping times), though the order doesn't matter in the final /etc/hosts file
    sorted_ips = sorted(ips.items(), key=lambda item: item[1])

    # Prepare the lines to add to /etc/hosts
    host_entries = []
    for i, (ip, _) in enumerate(sorted_ips, start=1):
        hostname = f"cf{i}.host"
        host_entries.append(f"{ip} {hostname}\n")

    # Backup the existing /etc/hosts file
    os.system("sudo cp /etc/hosts /etc/hosts.bak")

    # Read the existing /etc/hosts file
    with open("/etc/hosts", "r") as file:
        lines = file.readlines()

    # Optionally, you might want to remove any existing entries for cf*.host to avoid duplicates.
    lines = [line for line in lines if not any(f"cf{i}.host" in line for i in range(1, len(sorted_ips)+1))]

    # Append the new host entries
    lines.extend(host_entries)

    # Write the modified lines back to /etc/hosts
    with open("/etc/hosts", "w") as file:
        file.writelines(lines)

    print("Updated /etc/hosts file successfully.")

# Function to ping a host a specified number of times and return the minimum ping time
def ping_host_min(host, count):
    try:
        # Execute the ping command with the specified number of packets
        output = subprocess.check_output(["ping", "-c", str(count), host], universal_newlines=True)
        # Extract the ping times from the output
        min_ping_time = float('inf')  # Start with infinity as the initial minimum
        for line in output.splitlines():
            if "time=" in line:
                ping_time = float(line.split("time=")[-1].split(" ")[0])
                if ping_time < min_ping_time:
                    min_ping_time = ping_time
        # Return the minimum ping time found
        return min_ping_time if min_ping_time != float('inf') else None
    except subprocess.CalledProcessError:
        return None


if __name__ == "__main__":
    url = sys.argv[1] #your vless airport url

    content_b64 = requests.get(url)
    decoded_content = base64.b64decode(content_b64.content)

    lines = decoded_content.splitlines()

    ips = {}

    for l in lines:
        x = l.decode("utf-8")
        elems = x.split("://")
        scheme = elems[0]
        link  = elems[1]
        if scheme == "vless":
            if "0.01" in link:
                ip = link.split("?")[0].split("@")[1].split(":")[0]
                if ip in ips:
                    ips[ip] += 1
                else:
                    ips[ip] = 1

    # Dictionary to store the results
    ping_results = {}

    # Iterate over the ips dictionary and ping each host the specified number of times
    for host, count in ips.items():
        min_ping_time = ping_host_min(host, count)
        if min_ping_time is not None:  # Only include successful pings
            ping_results[host] = min_ping_time

    # Sort the results by ping value (lower first)
    sorted_ping_results = dict(sorted(ping_results.items(), key=lambda item: item[1]))


    # Print the sorted dictionary
    j=(json.dumps(sorted_ping_results))
    curr_ts = os.popen("date").read().strip("\n")
    out_line = curr_ts + " | " + j + "\n"
    f = open("/var/log/cf_ips.log", "a")
    f.write(out_line)
    print(out_line)
    #post to server if needed

    update_hosts_file(sorted_ping_results)