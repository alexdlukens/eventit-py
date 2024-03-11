import pathlib
import subprocess

import pytest
from pymongo import MongoClient

current_path = pathlib.Path(__file__)
port_forward_script_path = (
    current_path.parent.parent.parent / "scripts" / "port_forward_mongodb.sh"
)


@pytest.fixture
def get_minikube_mongo_uri():
    subprocess.Popen(port_forward_script_path)
    # Get the Minikube IP address
    minikube_ip_process = subprocess.Popen(["minikube", "ip"], stdout=subprocess.PIPE)
    minikube_ip, _ = minikube_ip_process.communicate()
    minikube_ip = minikube_ip.decode().strip()

    password = subprocess.Popen(
        'kubectl get secret mongodly-mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 -d',
        shell=True,
        stdout=subprocess.PIPE,
    )
    password, _ = password.communicate()
    password = password.decode("utf-8")

    mongo_uri = f"mongodb://root:{password}@127.0.0.1:27017/?authSource=admin"

    # ensure we can connect to the mongo client here
    mc = MongoClient(mongo_uri)
    mc.server_info()

    return mongo_uri
