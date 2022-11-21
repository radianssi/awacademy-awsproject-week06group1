# Container project
Run your own blog with Flask in AWS EKS and AWS RDS (PostreSQL). Group project to learn how to utilize AWS resources.

# Installation

### Initialize resources to AWS
Create virtual Python (3.10) enviroment, activate it and install depencies for initializiation. Run in CMD on project folder:
py -3.10 -m venv venv
.\venv\Scripts\activate
python -m pip install psycopg2
python -m pip install boto3

Run initialize.py on command line with these parameters (password must be at least 8 characters long):
python initialize.py yourdesiredusername yourdesiredpassword yourdesideredawsregion
(i.e. python initialize.py sieni sipul1keiTTo eu-central-1)

This will take ~2-3 minutes before everything is up and running.

This will create Security Group for RDS, RDS itself (PostgreSQL), create Secret in SecretsManager, create table in RDS dabatase and insert some test data to table.

It will use default VPC so if you have created more than one VPC in your region then it might fail.

### Create container, push it to ECR and update "image" value in deployment.yaml
Go to AWS ECR and create private repository with name group1blog. View push commands and type them in to the CMD one by one to create container and push it to AWS ECR.

After this open deployment.yaml and change "image" value from containers to your own ECR repository URI.

### Create EKS cluster for AWS
Install kubectl and eksctl.

To initiate EKS cluster install kubectl and eksctl. 
Use the command ekctl create cluster --name cluster-name --node-type t2.micro --nodes 2

eksctl will automatically create the cluster with VPC, subnets, nodegroup, nodes and other required components for you.

There will be an IAM role attached to the node group. In order for the node group to access the SecretsManager, you need to add the SecretsManager policy to the IAM role.

### Run deployment.yaml and service.yaml and get loab balancer's public address:
Run these commands in CMD:
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

After a while loab balancer will be online and you can find public address with this command:
kubectl get services -o wide

Go to that address and you should see your blog!