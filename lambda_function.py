import json
import boto3
import os
from datetime import datetime, timedelta

# import environment variables
limit = float(os.environ['limit'])
sns_topic = os.environ['sns_topic']


def calculate_deltas(values):
    deltas = []
    max_position = len(values)
    for i in range(1, max_position):
        if values[i] < values[i - 1]:
            deltas.append(values[i])
        else:
            deltas.append(values[i] - values[i - 1])
    return deltas


def lambda_handler(event, context):

    client = boto3.client('cloudwatch', region_name='us-east-1')

    response = client.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/Billing",
                        "MetricName": "EstimatedCharges",
                        "Dimensions": [
                            {
                                "Name": "Currency",
                                "Value": "USD"
                            }
                        ]
                    },
                    "Period": 3600,
                    "Stat": "Maximum",
                    "Unit": "None"
                }
            }
        ],
        StartTime=datetime.now() - timedelta(hours=24),
        EndTime=datetime.now(),
        ScanBy='TimestampAscending'
    )

    spent = 0

    for results in response["MetricDataResults"]:
        values = results["Values"]
        print(f"Timestamps of the datapoints:\n{results['Timestamps']}")
        print(f"Values of the datapoints:\n{values}")

        my_deltas = calculate_deltas(values)
        spent = sum(my_deltas)

        print(f"Deltas:\n{my_deltas}")
        print(f"Spent on the period:\n{spent}")

        if spent > limit:
            print("The threshold was breached, sending notification")
            sns_client = boto3.client('sns', region_name='us-east-1')
            message_body = {
                'default': {
                    'body': 'Daily spent limit breached',
                    'limit': limit,
                    'spent': "{:.2f}".format(spent)
                }
            }
            publish_response = sns_client.publish(
                TargetArn=sns_topic,
                Message=json.dumps({'default': json.dumps(message_body)}),
                MessageStructure='json'
            )
            print(publish_response)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'limit': limit,
            'spent': "{:.2f}".format(spent),
        })
    }
