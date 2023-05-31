# TA - FIRST ASSIGNMENT

## Deployment of BACKEND
To deploy this service run the following commands in the AWS shell

```bash
chmod +x deploy_server.sh
./deploy_server.sh
```
## Deployment of FRONTEND
To deploy the web interface run the following commands in the AWS shell

```bash
chmod +x deploy_frontend.sh
./deploy_frontend.sh
```
## AWS Manager
This project contains a script to manage different AWS services in a dew steps in order to ease the creation and removal of the instances. It is needed to place correctly the credentials in the .env file.

```bash
chmod +x AWS_manager.sh
./AWS_manager.sh
```
## Environment files
Please, pay attention to the content of the .env files when deploying the different AWS services.

## Python dependencies
The file `paquetes.txt` contains the needed Python depedencies that must be installed using the tool ``pip`` / ``pip3`` in order to make this project work properly.