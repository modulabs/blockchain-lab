# -*- coding: utf-8 -*-
import json

import boto3

with open('./conf/credentials.json', 'rU') as f:
  aws_credentials = json.load(f)
  access_key = aws_credentials['AccessKey']
  secret_key = aws_credentials['SecretKey']
  region = aws_credentials['Region']

  sns_client = boto3.client(
    'sns',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region,
  )

with open('./conf/config.json', 'rU') as f:
  config = json.load(f)
  topic_name = config['snsTopicName']
  topic_arn = config['snsTopicArn']

  alert_topic_name = config['snsAlertTopicName']
  alert_topic_arn = config['snsAlertTopicArn']


def send_notification(title, message):
  sns_client.publish(TopicArn=topic_arn, Subject=title, Message=message)


def send_alert_notification(title, message):
  sns_client.publish(TopicArn=alert_topic_arn, Subject=title, Message=message)
