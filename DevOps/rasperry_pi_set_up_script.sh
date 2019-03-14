sudo apt update -y && sudo apt upgrade -y
sudo apt install -y build-essential wget unzip python3 python3_dev python3-pip
sudo pip3 install pipenv

wget https://github.com/google/protobuf/releases/download/v3.2.0/protoc-3.2.0-linux-x86_64.zip
unzip protoc-3.2.0-linux-x86_64.zip
rm protoc-3.2.0-linux-x86_64.zip
mv bin /home/ubuntu

cd /home/ubuntu/PieCentral/runtime
pipenv install --dev
protoc -I ../ansible-protos --python_out=. ../ansible-protos/*.proto
