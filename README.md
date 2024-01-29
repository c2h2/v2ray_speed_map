# v2ray_speed_map

`v2ray_speed_map` is a Python tool designed to test the speed of various V2Ray subscription links. It generates an HTML report for each test, allowing for easy visualization of the performance of different V2Ray nodes. Additionally, the program maintains a history of old results for comparison and analysis over time.

## Sample Output:
+--------------------------+----------+-------------+------------+-----------------+
| comments                 | tcp_ping | google_ping | speed_mbps | ip              |
+--------------------------+----------+-------------+------------+-----------------+
| 🇨🇦 加拿大丨多伦多        | 560.2    | 1265.4      | 0.0        | 172.105.98.159  |
| 🇮🇳 印度丨孟买            | 343.5    | 1562.1      | 48.37      | 170.187.232.63  |
| 🇹🇼 台湾A丨Hinet丨流媒体  | 154.2    | 426.4       | 74.88      | 103.160.181.69  |
| 🇹🇼 台湾B丨Hinet丨流媒体  | 100.7    | 442.9       | 0.0        | 103.160.181.69  |
| 🇹🇼 台湾HKG丨原生流媒体   | 93.9     | 470.3       | 0.51       | FAILED          |
| 🇸🇬 新加坡A丨Lin丨流媒体  | 220.4    | 544.3       | 56.07      | 45.118.133.143  |
| 🇸🇬 新加坡B丨Lin丨流媒体  | 231.9    | 580.1       | 50.98      | FAILED          |
| 🇸🇬 新加坡丨HKG丨流媒体   | 101.3    | 435.8       | 74.41      | 103.47.101.62   |
| 🇯🇵 日本A丨Lin丨流媒体    | 206.5    | 688.9       | 83.92      | 139.162.120.173 |
| 🇯🇵 日本B丨BGP丨流媒体    | 210.4    | 934.5       | 95.16      | 157.254.193.170 |
| 🇯🇵 日本CMI丨移动优化     | 223.9    | 718.8       | 106.19     | 38.150.10.42    |
| 🇯🇵 日本C丨BGP丨流媒体    | 201.3    | 671.2       | 94.34      | 157.254.193.170 |
| 🇯🇵 日本丨原生丨流媒体    | 207.5    | 1039.9      | 79.53      | 153.242.227.1   |
| 🇹🇭 泰国丨暖武里府        | 234.3    | 785.1       | 58.02      | 45.136.253.71   |
| 🇦🇺 澳大利亚丨悉尼        | 419.0    | 1243.6      | 83.41      | 194.195.253.183 |
| 🇺🇲 美国A丨圣何塞丨流媒体 | 502.4    | 1837.0      | 92.68      | 165.3.122.200   |
| 🇺🇲 美国B丨圣何塞丨流媒体 | 471.2    | 2191.7      | 88.4       | 173.211.42.141  |
| 🇫🇮 芬兰丨流媒体          | 870.3    | 1293.6      | 64.21      | 109.204.233.150 |
| 🇬🇧 英国丨伦敦丨流媒体    | 582.7    | 1162.9      | 79.22      | 212.71.249.195  |
| 🇻🇳 越南丨原生丨流媒体    | 205.1    | 711.7       | 65.6       | 103.77.173.203  |
| 🇰🇷 韩国A丨Oracle丨流媒体 | 235.8    | 942.7       | 69.0       | 3.35.214.29     |
| 🇰🇷 韩国B丨Oracle丨流媒体 | 235.4    | 862.8       | 69.53      | 3.35.214.29     |
| 🇭🇰 香港A丨BGP丨流媒体    | 158.5    | 498.6       | 77.89      | 103.177.248.162 |
| 🇭🇰 香港A丨HKBN丨流媒体   | 194.1    | 450.0       | 80.34      | 223.16.1.177    |
| 🇭🇰 香港B丨BGP丨流媒体    | 160.4    | 771.4       | 74.01      | 103.177.248.162 |
| 🇭🇰 香港B丨HKBN丨流媒体   | 165.9    | 455.1       | 70.22      | 223.16.1.177    |
| 🇭🇰 香港C丨HKBN丨流媒体   | 98.9     | 454.2       | 70.48      | 223.16.1.177    |
| 🇭🇰 香港HKT丨10G丨流媒体  | 106.3    | 428.6       | 77.27      | 116.48.102.68   |
| 🇭🇰 香港丨HKT丨流媒体      | 107.3    | 452.1       | 76.52      | 116.48.102.68   |
+--------------------------+----------+-------------+------------+-----------------+

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.8 or higher. This version is needed to handle UTF-8/ASCII encoding issues properly.
- Access to V2Ray subscription links that you wish to test.

## Installation

To install `v2ray_speed_map`, follow these steps:

1. Clone the repository:
    git clone https://github.com/c2h2/v2ray_speed_map.git

2. Navigate to the project directory:
    cd v2ray_speed_map

3. Install the required Python packages:
    pip install -r requirements.txt


## Usage

To use `v2ray_speed_map`, follow these steps:

1. Edit the `config.json` file to include the V2Ray subscription links you wish to test.
2. Run the script:
    python3 v2ray_speed_map.py 
3. View the generated HTML reports in the `reports` directory. (LATER)
4. Check the `history` directory for past test results. (LATER)

## Contributing

Contributions to `v2ray_speed_map` are welcome. To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Create a new Pull Request.

