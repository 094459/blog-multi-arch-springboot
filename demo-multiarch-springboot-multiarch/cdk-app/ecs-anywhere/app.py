# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#!/usr/bin/env python3

from aws_cdk import core

from ecs_anywhere.ecs_anywhere_cicd import EcsAnywhereCICDStack
from ecs_anywhere.ecs_anywhere_vpc import EcsAnywhereVPCStack
from ecs_anywhere.ecs_anywhere_ecs import EcsAnywhereECSStack
from ecs_anywhere.ecs_anywhere_pipe import EcsAnywherePipeStack
from ecs_anywhere.ecs_anywhere_repo import EcsAnywhereLBStack


env_EU=core.Environment(region="eu-central-1", account="704533066374")
props = {
    'mydcexternalip': '80.42.49.11',
    'mydcinternalcidr' : '192.168.1.0/24',
    'awsvpccidr':'10.0.0.0/16',
    'ecsclustername':'mydc-ecs',
    'ecr-repo': 'demo-springboot-ecsanywhere',
    'code-repo' : 'demo-springboot-repo',
    'image-tag' : 'abcdef',
    'home-pi' : '192.168.1.99'
    }

#env_EU=core.Environment(region="eu-west-1", account="704533066374")

#props = {
#    'mydcexternalip': '80.42.49.11',
#    'mydcinternalcidr' : '192.168.1.0/24',
#    'awsvpccidr':'10.0.0.0/16',
#    'ecsclustername':'mydc-ecs',
#    #'ecr-repo': 'demo-multiarch-springboot-ecsanywhere',
#    'ecr-repo': 'demo-springboot-ecsanywhere',
#    #'code-repo' : 'demo-multiarch-springboot-multiarch',
#    'code-repo' : 'demo-springboot-repo',
#    'image-tag' : 'abcdef',
#    'home-pi' : '192.168.1.99'
#    }

app = core.App()

mydc_vpc = EcsAnywhereVPCStack(
    scope=app,
    id="ecs-anywhere-vpc",
    env=env_EU,
    props=props
)

mydc_lb = EcsAnywhereLBStack(
    scope=app,
    id="ecs-anywhere-lb",
    env=env_EU,
    vpc=mydc_vpc.vpc,
    props=props
)

mydc_ecs_cicd = EcsAnywhereCICDStack(
    scope=app,
    id="ecs-anywhere-cicd",
    env=env_EU,
    vpc=mydc_vpc.vpc,
    props=props  
)

mydc_ecs_pipe = EcsAnywherePipeStack(
    scope=app,
    id="ecs-anywhere-pipe",
    env=env_EU,
    vpc=mydc_vpc.vpc,
    props=props  
)

mydc_ecs = EcsAnywhereECSStack(
    scope=app,
    id="ecs-anywhere-cfn",
    env=env_EU,
    vpc=mydc_vpc.vpc,
    props=props
)

app.synth()