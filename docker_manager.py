import os
from dotenv import load_dotenv
import docker
from datetime import datetime

load_dotenv()

docker_host = os.getenv('DOCKER_HOST')

if docker_host:
    client = docker.DockerClient(base_url=docker_host)
    print(f"Connecting to Docker host at {docker_host}")
else:
    client = docker.from_env()
    print("Connecting to Docker host at default location")

def format_ports(ports):
    formatted_ports = []
    seen_host_ports = set()
    if ports:
        for internal_port, mappings in ports.items():
            if mappings:
                for mapping in mappings:
                    host_port = mapping['HostPort']
                    if host_port not in seen_host_ports:
                        seen_host_ports.add(host_port)
                        formatted_ports.append(f"{host_port}:{internal_port.split('/')[0]}")
    return formatted_ports

def format_date(date):
    return datetime.strptime(date[:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')


def list_containers():
    containers = client.containers.list(all=True)

    container_info = [{
        'Id': container.id,
        'Image': container.image.tags,
        'Created': format_date(container.attrs['Created']),
        'Status': container.status,
        'Ports': format_ports(container.attrs['NetworkSettings']['Ports']),
        'Names': container.attrs['Name'][1:]
    } for container in containers]

    for container in container_info:
        print(f"Container ID: {container['Id']} | Image: {container['Image']} | Created: {container['Created']} | Status: {container['Status']} | Ports: {container['Ports']} | Names: {container['Names']}")
        
    return container_info

def stop_container(container_id):
    container = client.containers.get(container_id)
    container.stop()
    return f"Container {container_id} stopped."

def start_container(container_id):
    container = client.containers.get(container_id)
    container.start()
    return f"Container {container_id} started."

def get_container_logs(container_id):
    container = client.containers.get(container_id)
    return container.logs().decode('utf-8')

