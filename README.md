# stockholm-ai

## Introduction
The python notebook Sample Code contains a running example of setting up a working example of serving an MNIST model with keras, tensorflowserving, and flask on AWS ECS.

### Code should:

    - Train keras model with MNIST.
    - Convert model to TF format
    - Build docker image and push it to AWS ECR (Elastic Container Registry)
    - Register a new task definition (task_definition.json)
    - Create a new service on ECS (Elastic Container Service) running.
    - Deregister old task definitions
    - Rebuild image, update service with new task definition and redeploy code. (Optional)

### Heads Up:

    - Using a mix of boto3 and AWS CLI. Not really ideal but did not have time to rewrite to boto3.

## Requirements.

- Install python requirements with pip3 install -r requirements.txt
- Install Jupyter Notebook
- Installed Docker (https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- Installed & configured AWS CLI (https://aws.amazon.com/cli/)
- AWS Elastic Load Balancer setup as an Application Load Balancer with a listener on 443 (and an SSL certificate)
- AWS Elastic Container Service cluster setup and configured

