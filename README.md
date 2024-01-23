# v2ray_speed_map

`v2ray_speed_map` is a Python tool designed to test the speed of various V2Ray subscription links. It generates an HTML report for each test, allowing for easy visualization of the performance of different V2Ray nodes. Additionally, the program maintains a history of old results for comparison and analysis over time.

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

