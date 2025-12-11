import os

from aws_cdk import Duration, Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_cloudwatch_actions as cloudwatch_actions
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
from constructs import Construct


class CloudwatchAlarmStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        instance_id = os.environ["INSTANCE_ID"]
        print("Set Alarm for ", instance_id)

        cpu_alarm = cloudwatch.Alarm(
            self,
            "CpuHigh",
            metric=cloudwatch.Metric(
                namespace="AWS/EC2",
                metric_name="CPUUtilization",
                dimensions_map={"InstanceId": instance_id},
                period=Duration.minutes(1),
                statistic="Average",
            ),
            threshold=70,
            evaluation_periods=2,
            alarm_description="CPU > 70% trong 2 phút",
        )

        network_in_alarm = cloudwatch.Alarm(
            self,
            "NetworkInHigh",
            metric=cloudwatch.Metric(
                namespace="AWS/EC2",
                metric_name="NetworkIn",
                dimensions_map={"InstanceId": instance_id},
                period=Duration.minutes(1),
                statistic="Sum",
            ),
            threshold=50000000,
            evaluation_periods=1,
            alarm_description="Network In vượt 50MB trong 1 phút",
        )

        ram_alarm = cloudwatch.Alarm(
            self,
            "RamHigh",
            metric=cloudwatch.Metric(
                namespace="CWAgent",
                metric_name="mem_used_percent",
                dimensions_map={"InstanceId": instance_id},
                period=Duration.minutes(1),
                statistic="Average",
            ),
            threshold=80,
            evaluation_periods=2,
            alarm_description="RAM vượt ngưỡng 80%",
        )

        alarm_topic = sns.Topic(
            self,
            "EC2AlarmTopic",
            display_name="EC2 Monitoring Alerts"
        )

        email_subscriptions: list[str] = os.environ['EMAIL_SUBSCRIPTIONS'].split(',')
        for email in email_subscriptions:
            alarm_topic.add_subscription(
                sns_subscriptions.EmailSubscription(email.strip())
            )

        action = cloudwatch_actions.SnsAction(alarm_topic)

        cpu_alarm.add_alarm_action(action)
        network_in_alarm.add_alarm_action(action)
        ram_alarm.add_alarm_action(action)
