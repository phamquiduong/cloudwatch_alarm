import aws_cdk as cdk
from dotenv import load_dotenv

from cloudwatch_alarm.cloudwatch_alarm_stack import CloudwatchAlarmStack

if not load_dotenv():
    raise FileNotFoundError('.env file not found')

app = cdk.App()
CloudwatchAlarmStack(app, "CloudwatchAlarmStack")

app.synth()
