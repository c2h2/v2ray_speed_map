import requests
import time

def download_file(url):
    start_time = time.time()
    response = requests.get(url, stream=True)
    
    total_length = response.headers.get('content-length')

    if total_length is None:  # no content length header
        print("Couldn't retrieve the file")
    else:
        total_length = int(total_length)
        bytes_downloaded = 0

        for data in response.iter_content(chunk_size=4096):
            bytes_downloaded += len(data)

        end_time = time.time()
        duration = end_time - start_time
        speed_bps = bytes_downloaded / duration
        speed_mbps = speed_bps / (1024 * 1024)  # Convert to Megabits per second

        print(f"Download speed: {speed_mbps:.2f} Mbps")

# Example URL of a large file
test_url = 'http://ipv4.download.thinkbroadband.com/100MB.zip'
download_file(test_url)
