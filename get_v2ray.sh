rm -rf v2ray
mkdir -p v2ray
#wget -O v2ray/v2ray.tar.gz https://github.com/teddysun/v2ray-plugin/releases/download/v5.13.0/v2ray-plugin-linux-amd64-v5.13.0.tar.gz
#tar -zxvf v2ray/v2ray.tar.gz -C v2ray
cd v2ray

wget -O v2ray.zip https://github.com/v2fly/v2ray-core/releases/download/v5.12.1/v2ray-linux-64.zip
if [ $? -ne 0 ]; then
    unzip v2ray.zip  # Add this line to extract the downloaded v2ray.zip file
    chmod +x v2ray
    chmod +x v2ray
    echo "v2ray download successed"
    exit 0
else
    echo "v2ray download failed"
    exit 1
fi
