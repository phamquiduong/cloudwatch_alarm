from aws_cdk import Duration, Stack
from aws_cdk import aws_cloudwatch as cloudwatch
from aws_cdk import aws_cloudwatch_actions as cloudwatch_actions
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
from aws_cdk.aws_cloudwatch_actions import SnsAction
from constructs import Construct


class CloudwatchAlarmStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, configs: list[dict], **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        self.configs = configs

        for config in configs:
            self.set_alarm_for_instance(config)

    def _id_suffix(self, instance_id: str) -> str:
        return instance_id.replace('-', '')

    def set_alarm_for_instance(self, config: dict):
        instance_id: str = config['instance_id']
        subscriptions: dict = config['subscriptions']
        id_suffix = self._id_suffix(instance_id)

        action = self._create_sns_action(
            instance_id=instance_id,
            id_suffix=id_suffix,
            subscriptions=subscriptions,
        )

        self._set_cpu_alarm(instance_id, id_suffix).add_alarm_action(action)            # type:ignore
        self._set_ram_alarm(instance_id, id_suffix).add_alarm_action(action)            # type:ignore
        self._set_disk_alarm(instance_id, id_suffix).add_alarm_action(action)           # type:ignore
        self._set_network_in_alarm(instance_id, id_suffix).add_alarm_action(action)     # type:ignore
        self._set_network_out_alarm(instance_id, id_suffix).add_alarm_action(action)    # type:ignore

    def _create_sns_action(self, instance_id: str, id_suffix: str, subscriptions: dict) -> SnsAction:
        alarm_topic = sns.Topic(
            self,
            f'EC2AlarmTopic-{id_suffix}',
            display_name=f'EC2 Monitoring Alerts for {instance_id}',
        )

        for email in subscriptions.get('email', []):
            alarm_topic.add_subscription(sns_subscriptions.EmailSubscription(email.strip()))    # type:ignore

        return cloudwatch_actions.SnsAction(alarm_topic)                                        # type:ignore

    def _set_cpu_alarm(self, instance_id: str, id_suffix: str) -> cloudwatch.Alarm:
        return cloudwatch.Alarm(
            self,
            f'CpuHigh-{id_suffix}',
            metric=cloudwatch.Metric(
                namespace='EC2/Custom',
                metric_name='cpu_usage_idle',
                dimensions_map={'InstanceId': instance_id},
                period=Duration.minutes(1),
                statistic='Average',
            ),
            threshold=20,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description='CPU usage exceeds 80% (idle below 20%)',
        )

    def _set_ram_alarm(self, instance_id: str, id_suffix: str) -> cloudwatch.Alarm:
        return cloudwatch.Alarm(
            self,
            f'RamHigh-{id_suffix}',
            metric=cloudwatch.Metric(
                namespace='EC2/Custom',
                metric_name='mem_used_percent',
                dimensions_map={'InstanceId': instance_id},
                period=Duration.minutes(1),
                statistic='Average',
            ),
            threshold=80,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description='RAM usage exceeds 80%',
        )

    def _set_disk_alarm(self, instance_id: str, id_suffix: str) -> cloudwatch.Alarm:
        return cloudwatch.Alarm(
            self,
            f'DiskHigh-{id_suffix}',
            metric=cloudwatch.Metric(
                namespace='EC2/Custom',
                metric_name='disk_used_percent',
                dimensions_map={
                    'InstanceId': instance_id,
                    'path': '/',
                    'device': 'xvda1',
                    'fstype': 'xfs',
                },
                period=Duration.minutes(1),
                statistic='Average',
            ),
            threshold=85,
            evaluation_periods=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description='Root disk usage exceeds 85%',
        )

    def _set_network_in_alarm(self, instance_id: str, id_suffix: str) -> cloudwatch.Alarm:
        return cloudwatch.Alarm(
            self,
            f'NetworkInZero-{id_suffix}',
            metric=cloudwatch.Metric(
                namespace='EC2/Custom',
                metric_name='net_bytes_recv',
                dimensions_map={
                    'InstanceId': instance_id,
                    'interface': 'eth0',
                },
                period=Duration.minutes(1),
                statistic='Sum',
            ),
            threshold=1,
            evaluation_periods=3,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            alarm_description='No incoming network traffic detected',
        )

    def _set_network_out_alarm(self, instance_id: str, id_suffix: str) -> cloudwatch.Alarm:
        return cloudwatch.Alarm(
            self,
            f'NetworkOutZero-{id_suffix}',
            metric=cloudwatch.Metric(
                namespace='EC2/Custom',
                metric_name='net_bytes_sent',
                dimensions_map={
                    'InstanceId': instance_id,
                    'interface': 'eth0',
                },
                period=Duration.minutes(1),
                statistic='Sum',
            ),
            threshold=1,
            evaluation_periods=3,
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_THRESHOLD,
            alarm_description='No outgoing network traffic detected',
        )
