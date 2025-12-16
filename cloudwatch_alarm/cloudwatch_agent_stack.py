from aws_cdk import Stack
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class CloudwatchAgentStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        with open('cw-agent.json', encoding='utf-8') as f:
            cw_agent_config = f.read()

        ssm.StringParameter(
            self,
            'CwAgentConfig',
            parameter_name='/cwagent/ec2/app/config',
            string_value=cw_agent_config,
        )

        ssm.CfnAssociation(
            self,
            'InstallCwAgent',
            name='AWS-ConfigureAWSPackage',
            parameters={
                'action': ['Install'],
                'name': ['AmazonCloudWatchAgent'],
            },
            targets=[{
                'key': 'tag:CwAgent',
                'values': ['enabled'],
            }],
        )

        ssm.CfnAssociation(
            self,
            'ConfigureCwAgent',
            name='AmazonCloudWatch-ManageAgent',
            parameters={
                'action': ['configure'],
                'mode': ['ec2'],
                'optionalConfigurationSource': ['ssm'],
                'optionalConfigurationLocation': ['/cwagent/ec2/app/config'],
                'optionalRestart': ['yes'],
            },
            targets=[{
                'key': 'tag:CwAgent',
                'values': ['enabled'],
            }],
        )

        ssm.CfnAssociation(
            self,
            'UninstallCwAgent',
            name='AWS-ConfigureAWSPackage',
            parameters={
                'action': ['Uninstall'],
                'name': ['AmazonCloudWatchAgent'],
            },
            targets=[{
                'key': 'tag:CwAgent',
                'values': ['disabled'],
            }],
        )
