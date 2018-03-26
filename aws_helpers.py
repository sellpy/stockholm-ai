"""Helpers for making aws calls a bit easier."""
import boto3

# Assumes a load balancer and listener is in place.


def create_repository(repository_name="stockholm-ai"):
    """Create new ecr repository with lifecycle policy."""
    ecr_client = boto3.client("ecr")

    # This is not very elegant.
    try:
        repo = ecr_client.create_repository(repositoryName=repository_name)
        lifecycle_policy = """{
          "rules": [
            {
              "rulePriority": 10,
              "description": "Delete untagged",
              "selection": {
                "tagStatus": "untagged",
                "countType": "imageCountMoreThan",
                "countNumber": 3
              },
              "action": {
                "type": "expire"
              }
            }
          ]
        }"""
        ecr_client.put_lifecycle_policy(
            repositoryName=repository_name,
            lifecyclePolicyText=lifecycle_policy)
    except:
        repo = ecr_client.describe_repositories(
            repositoryNames=[repository_name])

    return repo


def setup_elb(service,
              version,
              load_balancer_name="sellpy-services",
              service_path='services.dev.sellpy.net'):
    """Setup target in ELB loadbalancer."""
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
    elb_rules = client.describe_rules(
        ListenerArn=listner_arn)

    new_rule_condition = [
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

    prio = 0
    for rule in elb_rules["Rules"]:
        conditions = rule["Conditions"]
        if ((new_rule_condition[0] in conditions) &
           (new_rule_condition[1] in conditions)):
            return target_group_arn
        if rule["Priority"] != "default":
            prio = max(prio, int(rule["Priority"]))
    prio += 1

    response = client.create_rule(
        ListenerArn=listner_arn,
        Conditions=new_rule_condition,
        Priority=prio,
        Actions=[
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_arn
            },
        ]
    )
    return target_group_arn


# ---- ECS ----
def deregister_old_taskdefinitions(service):
    """Remove old task definitions."""
    ecs_client = boto3.client('ecs')

    task_defs = ecs_client.list_task_definitions(
        familyPrefix=service,
        status='ACTIVE',
        sort='ASC',
        maxResults=100
    )
    for revision in task_defs["taskDefinitionArns"][0:-1]:
        print()
        ecs_client.deregister_task_definition(
            taskDefinition=revision.split("/")[-1])


def create_ecs_service(cluster,
                       service,
                       task_definition_family,
                       target_group_arn,
                       service_count=1,
                       launch_type='EC2'):
    """Create ecs service for serving whatever you need."""
    ecs_client = boto3.client('ecs')

    if service in ecs_client.list_task_definition_families()["families"]:
        task_def = ecs_client.list_task_definitions(
            familyPrefix=task_definition_family,
            sort='DESC')["taskDefinitionArns"][0]

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
        launchType=launch_type,
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
        healthCheckGracePeriodSeconds=15
    )
    return response
