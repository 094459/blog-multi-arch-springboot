# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    core
)

class EcsAnywhereVPCStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
  
        # Create VPC networking environment
        # Public subnet/ "private"(isolated) subnet
        # Customer Gateway and Virtual Private Gateway
        # Site to Site VPN Connection

        self.vpc = ec2.Vpc(
            self,
            id="mydc-vpn-vpc",
            cidr=f"{props['awsvpccidr']}",
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", cidr_mask=24,
                    reserved=False, subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(
                    name="private", cidr_mask=24,
                    #reserved=False, subnet_type=ec2.SubnetType.ISOLATED)
                    reserved=False, subnet_type=ec2.SubnetType.PRIVATE)
            ],
            max_azs=2,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            vpn_gateway=True
        )

        self.vpc.add_vpn_connection(
            id="mydcvpn",
            ip=f"{props['mydcexternalip']}",
            static_routes=[f"{props['mydcinternalcidr']}"]
        )

        
        core.CfnOutput(
            self,
            id="VPCId",
            value=self.vpc.vpc_id,
            description="VPC ID",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:vpc-id"
        )

        core.CfnOutput(
            self,
            id="VPGId",
            value=self.vpc.vpn_gateway_id,
            description="VPG ID"
        )


