# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ssm as ssm,
    aws_logs as log,
    aws_codecommit as codecommit,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    core
)

class EcsAnywhereCICDStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the CI/CD pipeline here

        # Create a new ECS Cluster with auto scaling groups that
        # contain x86 and Graviton2 instance types

        ecscluster_role = iam.Role(
            self,
            f"{props['ecsclustername']}-ecsrole",
            assumed_by=iam.ServicePrincipal("ssm.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")]
        )
        ecscluster_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2ContainerServiceforEC2Role"))

        ecscluster = ecs.Cluster(
            self,
            f"{props['ecsclustername']}-ecscluster",
            vpc=vpc
        )

        # store ECS Cluster name in Parameter store so we can retrieve it later

        ecscluster_name = ssm.StringParameter(
            self,
            "ECSClusterName",
            parameter_name="/demo/ecsanywhere/clustername",
            string_value=ecscluster.cluster_name,
            tier=ssm.ParameterTier.STANDARD
        )

        ecscluster_name = ssm.StringParameter(
            self,
            "ECSClusterShortName",
            parameter_name="/demo/ecsanywhere/shortcn",
            string_value=f"{props['ecsclustername']}",
            tier=ssm.ParameterTier.STANDARD
        )

        ## If you want to just set up a single ASG with a single
        ## instance type, you can use this instead

        #ecscluster_asg = autoscaling.AutoScalingGroup(
        #    self,
        #    f"{props['ecsclustername']}-asg",
        #    vpc=vpc,
        #    instance_type=ec2.InstanceType("t4g.xlarge"),
        #    machine_image=ecs.EcsOptimizedImage.amazon_linux2(ecs.AmiHardwareType.ARM),
        #    desired_capacity=3
        #)

        #ecscluster.add_auto_scaling_group(ecscluster_asg)

        # Create two ASGs which have two different instance types
        # This will allow you to deploy and test against x86 and arm

        ecscluster.add_capacity(
            "x86AutoScalingGroup",
            instance_type=ec2.InstanceType("t2.xlarge"),
            desired_capacity=1
        )
        ecscluster.add_capacity(
            "Graviton2AutoScalingGroup",
            instance_type=ec2.InstanceType("t4g.large"),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(ecs.AmiHardwareType.ARM),
            desired_capacity=1
        )

        ec2_task_definition = ecs.Ec2TaskDefinition(
            self,
            f"{props['ecsclustername']}-SpringBootTaskDef",
            family="springboot-cicd",
            network_mode=ecs.NetworkMode.AWS_VPC
            )
    
        # select ECR repo and starting container image
        # we set these in the properties file but we also can get this from the parameter store

        #demo_app_image = ssm.StringParameter.from_string_parameter_attributes(
        #    self,
        #    "ContainerTagLatest",
        #    parameter_name="/demo/ecsanywhere/latestimage"
        #).string_value
       
        springboot_repo = ecr.Repository.from_repository_name(self, "springbootecrrepo", repository_name=f"{props['ecr-repo']}")
        springboot_image = ecs.ContainerImage.from_ecr_repository(springboot_repo, f"{props['image-tag']}")

        # Create log group

        log_group = log.LogGroup(
            self,
            "LogGroup",
            log_group_name=f"{props['ecsclustername']}-loggrp"
        )

        container = ec2_task_definition.add_container(
            "SpringBootCICD",
            image=springboot_image,
            memory_limit_mib=1024,
            cpu=100,
            # Configure CloudWatch logging
            logging=ecs.LogDrivers.aws_logs(stream_prefix=f"{props['ecsclustername']}-logs",log_group=log_group),
            essential=True
            )
        
        port_mapping = ecs.PortMapping(
            container_port=8080,
            # Disable if using AWS_VPC Network mode
            # host_port=8080,
            protocol=ecs.Protocol.TCP
        )

        container.add_port_mappings(port_mapping)

        springboot_security_group = ec2.SecurityGroup(
            self,
            "Springboot http access",
            vpc=vpc
        )

        springboot_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80)
        )

        service = ecs.Ec2Service(
            self,
            "service",
            cluster=ecscluster,
            task_definition=ec2_task_definition,
            desired_count=2,
            #enable_execute_command=True
            security_group=springboot_security_group

        )

        # store ECS Service name in Parameter store so we can retrieve it later

        ecscluster_name = ssm.StringParameter(
            self,
            "ECSServiceName",
            parameter_name="/demo/ecsanywhere/servicename",
            string_value=service.service_name,
            tier=ssm.ParameterTier.STANDARD
        )

        lb = elbv2.ApplicationLoadBalancer(
            self,
            "LB",
            vpc=vpc,
            internet_facing=True
        )
        
        listener = lb.add_listener(
            "PublicListener",
            port=80,
            open=True)
        
        listener.add_targets(
            "ECS",
            port=80,
            targets=[service]
        )

        core.CfnOutput(
            self,
            id="LoadBalancerEndpoint",
            value=lb.load_balancer_dns_name,
            description="DNS name of application load balancer of your ECS Cluster"
        )