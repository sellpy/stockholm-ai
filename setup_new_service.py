import os
import subprocess
from aws_helpers import create_repository, setup_elb, create_ecs_service, deregister_old_taskdefinitions

version = 1
service_path = 'services.dev.sellpy.net'
service = "stockholm-ai"
env = "dev"
cluster = "microservices"
load_balancer_name = "sellpy-services"

# Create an image repository for storing docker files.
create_repository(service)

subprocess.call(
	"eval $( aws ecr get-login --no-include-email)",
	shell=True)
subprocess.call(
	"docker build -t temp_image .",
	shell=True)
subprocess.call(
	"docker tag temp_image 966836717103.dkr.ecr.eu-west-1.amazonaws.com/" + ":".join([service, env]), 
	shell=True)
subprocess.call(
	"docker push 966836717103.dkr.ecr.eu-west-1.amazonaws.com/" + ":".join([service, env]),
	shell=True)
subprocess.call(
	"aws ecs register-task-definition --cli-input-json file://task_definition_2.json --region eu-west-1",
	shell=True)