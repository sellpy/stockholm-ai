import boto3
import sys

version = 1
service_path = 'services.dev.sellpy.net'
service = "tester_dev"
cluster = "microservices"
load_balancer_name = "sellpy-services"

# Assumes a load balancer and listener is in place.

client = boto3.client('elbv2')

# Create a target group for the new services
response = client.create_target_group(
    Name=service,
    Protocol='HTTP',
    Port=80,
    VpcId='vpc-ec384689',
    HealthCheckProtocol='HTTP',
    HealthCheckPort='traffic-port',
    HealthCheckPath='/health_check',
    HealthCheckIntervalSeconds=30,
    HealthCheckTimeoutSeconds=5,
    HealthyThresholdCount=2,
    UnhealthyThresholdCount=2,
    TargetType='instance'
)

target_group_arn = response["TargetGroups"][0]["TargetGroupArn"]

# Fetch load balancer adata
load_balancers = client.describe_load_balancers()["LoadBalancers"]

for load_balancer in load_balancers:
    if load_balancer["LoadBalancerName"] == load_balancer_name:
        lb_arn = load_balancer["LoadBalancerArn"]
        break

listeners = client.describe_listeners(LoadBalancerArn=lb_arn)["Listeners"]
# Only have one listener (port 443)
listner_arn = listeners[0]["ListenerArn"]

# Fetch rules for load balancer
elb_rules = client.describe_rules(ListenerArn=listner_arn)

rule_conditions = [
    {
        'Field': 'host-header',
        'Values': [
            service_path,
        ]
    },
    {
        'Field': 'path-pattern',
        'Values': [
            '/v' + str(version) + '/' + service + "*",
        ]
    },
]

max_prio = 0
for rule in elb_rules["Rules"]:
    if rule["Priority"] != "default":
        max_prio = max(max_prio, int(rule["Priority"]))


response = client.create_rule(
    ListenerArn=listner_arn,
    Conditions=rule_conditions,
    Priority=max_prio + 1,
    Actions=[
        {
            'Type': 'forward',
            'TargetGroupArn': target_group_arn
        },
    ]
)

# ---- ECS ----

ecs_client = boto3.client('ecs')

if service in ecs_client.list_task_definition_families()["families"]:
    task_def = ecs_client.list_task_definitions(
        familyPrefix=service, sort='DESC')["taskDefinitionArns"][0]

response = ecs_client.create_service(
    cluster=cluster,
    serviceName=service,
    taskDefinition=task_def,
    loadBalancers=[
        {
            'targetGroupArn': target_group_arn,
            'containerName': service,
            'containerPort': 8080
        },
    ],
    desiredCount=1,
    launchType='EC2',
    deploymentConfiguration={
        'maximumPercent': 200,
        'minimumHealthyPercent': 50
    },
    placementStrategy=[
        {
            'type': 'spread',
            'field': 'attribute:ecs.availability-zone'
        },
    ],
    healthCheckGracePeriodSeconds=120
)
