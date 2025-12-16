import aws_cdk as cdk
import yaml

from cloudwatch_alarm.cloudwatch_agent_stack import CloudwatchAgentStack
from cloudwatch_alarm.cloudwatch_alarm_stack import CloudwatchAlarmStack

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

app = cdk.App()
CloudwatchAgentStack(app, 'CloudwatchAgentStack')
CloudwatchAlarmStack(app, 'CloudwatchAlarmStack', configs=config['ec2'])

app.synth()
