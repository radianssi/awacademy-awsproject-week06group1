# Container project

To initiate EKS cluster install kubectl and eksctl. 
Use the command ekctl create cluster --name cluster-name --node-type t2.micro --nodes 2

eksctl will automatically create the cluster with VPC, subnets, nodegroup, nodes and other required
components for you.
