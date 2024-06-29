
# Network Manager

Network manager is a tool developed to simplify the task of monitoring all your services and containers.



## Deployment with docker

Make sure you have exposed the Docker API through tcp

### Docker

```bash
docker run -d \
  --name network_manager \
  --network host \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e DOCKER_HOST={IP_TO_DOCKER_MACHINE} \
  frogoman/network_manager:latest

```

### Docker compose

```yml
version: '3'
services:
  network_manager:
    image: frogoman/network_manager:latest
    container_name: network_manager
    network_mode: "host"
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - DOCKER_HOST={IP_TO_DOCKER_MACHINE} # Replace with IP:Port for Docker API
```



## Local instalation

To install the project and run it bare bones in a system follow:

0 - Make sure you have exposed the Docker API through tcp

1 - Clone the repository
```bash
git clone https://github.com/Frogoman/PFG-Network_Manager
```

2 - Go to the project directory
```bash
  cd PFG-Network_Manager
```

3 - Install requirements
```bash
  pip install -r requirements.txt
```

4 - Add the .env file with the DOCKER_HOST variable pointing to the tcp connection for the Docker API

5 - Run the project
```bash
  flask run --host=0.0.0.0
```



## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`DOCKER_HOST` : Address to tcp connection to the Docker API



## Roadmap

- Add Proxmox support

- Allow the user to create new containers from the interface

- Add functionality for multiple color themes

