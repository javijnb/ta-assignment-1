# TA - FIRST ASSIGNMENT

## Environment files
Please, pay attention to the content of the .env files when deploying the different AWS services.

## Grant permission to scripts

```bash
chmod +x ./Scripts/*
```

## AWS Manager
This project contains a script to manage different AWS services in few steps in order to ease the creation and removal of the instances. It is needed to place correctly the credentials in the .env file.

```bash
chmod +x AWS_manager.sh
./AWS_manager.sh
```

## Deployment of BACKEND
To deploy this service run the following commands in the AWS shell of the EC2 instances that run the Backend software:

```bash
chmod +x deploy_server.sh
sudo yum install python pip
pip3 install -r requirements.txt
./deploy_backend.sh
```

After this, it is needed to open the port 8000 to the outside. Head to the backend instances, Security, click in the Security Group ID, and add a new Enter Rule:

```
Type > TCP custom
Port > 8000
Origin > 0.0.0.0/0
Name > Backend
```

## Deployment of FRONTEND
To deploy the web interface run the following commands in the AWS shell of the EC2 instance that contains the Frontend software:

```bash
chmod +x deploy_frontend.sh
sudo yum install python pip
pip3 install flask
./deploy_frontend.sh
```

After this, it is needed to open the port 5000 to the outside. Head to the frontend instance, Security, click in the Security Group ID, and add a new Enter Rule:

```
Type > TCP custom
Port > 5000
Origin > 0.0.0.0/0
Name > Frontend
```

## Python dependencies
In case you need to run the Backend locally, install the required dependencies using:

```bash
pip install -r requirements.txt
```
