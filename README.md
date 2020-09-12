# aws-lambda-dailybillingalert

# Configuring a daily billing alert
A Lambda function to calculate the daily billing change.
SNS Topic to send us alerts if we breach our spending limit.
IAM Role to have the correct permissions to run the lambda and invoke the SNS topic.
CloudWatch Event Rules to set up a daily schedule to invoke the Lambda function.
We will also look at the CloudWatch Log Groups to monitor our Lambda function.

# SNS topic notification
The first step is creating the Simple Notification Service (SNS). This allows AWS to send and receive notifications. For our daily billing alert, we need to receive an email notification when we breach our daily limit.Navigate to SNS through the Services. Start by creating a Topic through just adding a name. Once the topic is created, click Create a Subscription. This allows us to choose “email” and set the email address. A confirmation email will be sent, which will have a link to confirm your email address. In the details window, make a note of the ARN. This will be required when creating the IAM role.

# Lambda function
We will now focus on the Lambda. From the Lambda landing page, select create function.
Lambda creation for billing alerts
Lambda creation for billing alerts

We need to fill in some basic information to create our Lambda function template. For the Function name, add a name that will be relevant to the Lambda. I’ve used Daily_Billing_Alerts. Change the runtime to Python 3.8. For the Execution role choose Create a new role with basic Lambda permissions. At this point, the Lambda will create an execution role. In this example, ours is named Daily_Billing_Alerts-role-7rseajla. Permissions to upload logs to Amazon CloudWatch Logs are set. This is something to which we will add shortly.Now click Create function.NOTE: We will be using Python to create our Lambda function, but I won’t be focusing too much on the code itself. Please visit my GitHub pages to download the Python 3.8 code used in this example: .Once the Lambda function is created, we will be amending the following three areas within the Lambda: the Function code, Environment variables and Execution role.Let us start with adding the Function code. Copy and paste the Python code into the Function code under lambda_function.

To allow some flexibility in the function, we will create two environment variables called limit and sns_topic. The limit variable will be the amount you want to be notified about when it is breached. So, this could be $10, $10,000 or $1,000,000! For the purpose of this demo, I will set the limit to 0.20, to allow for alerts to be triggered. (I try and keep my own account down to a minimal amount!). The sns_topic variable will hold the ARN of our SNS topic.

The last part we need to configure is to add to the role created by the Lambda function. Under the Execution role, you will see your role. Clicking on View the Daily_Billing_Alerts-role-7rseajla will take you to the summary of the role in IAM.
Execution role and changing existing role
Execution role and changing existing role

From here, select add inline policy. Then, choose JSON.Visual editor or JSONPaste in the following JSON code, making sure you change the resource for SNS to the ARN of your SNS topic.
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudwatch:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:*"
            ],
            "Resource": "arn:aws:sns:us-east-1:************:NotifyMe"
        }
    ]
}

This will allow access to CloudWatch and full access to our SNS topic.
Metric details
One part of the python code I want to briefly talk about is the metric data. The below metric data is added in JSON format, but how do we know what metric details to use or even find? 
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
        ]

One of the ways to do this is through CloudWatch itself. I have highlighted two areas. The first is the Metric option on the left-hand side. This will navigate you to the below screen. The second is the current metrics available to use/look at. As you use more features in AWS, more metrics become available. I have highlighted Billing, as this is the metric we are using.


On clicking Billing, you will be presented with a couple more subheadings.
Additional metrics under the billing metric
Additional metrics under the billing metric

The metric we need for this Lambda is under Total Estimated Charge. Looking at the metric name I’ve indicated, you’ll notice EstimatedCharges. If you recall, this was the name used in the Python code.
Drilling down to the metric required
Drilling down to the metric required

Again, I’ve highlighted a couple of steps to follow. First off, make sure the metric is ticked, and then select the Graphed metrics tab. This will allow us to adjust our metric criteria.
Ticking the metric to see data
Ticking the metric to see data

I’ve clicked on the down arrow and changed the time period to 1 Hour. Click the Source tab.
Adjusting our metric criteria
Adjusting our metric criteria

Now, here is the interesting part. If we compare the below information to our Python code snippet, we can see the same metric details.Let’s look at a portion of the JSON code again:
Metric": {
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
                    "Stat": "Maximum"
1
2
3
4
5
6
7
8
9
10
11
12
Metric": {
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
                    "Stat": "Maximum"
The metric data in the JSON uses the same values as the Period and Stat attributes.
Metric source information
Metric source information

This is an excellent way to drill down to the information we need, as CloudWatch does the hard work for us! I highly recommend exploring these metrics if you are looking to do some interesting stuff with Lambda!
Setting a CloudWatch Event Rule to schedule Lambda execution
As the Lambda is not triggered by an event, we need to create a schedule to invoke the execution. From the CloudWatch page, click on Rules below Event on the left-hand side.The Create rule step screen will appear.
Creating the event rule to trigger Lambda

To help with clarity, I have highlighted six areas:
The first one is to show the Rules option below Event. This is how we bring up the above screen.
Here is how we trigger our Lambda. We are using a schedule to change the option to this.
Next is how frequently we want our schedule to execute. We are looking for once a day, so amend this to 1 Day.
A sample event will be available to use. Copy and paste this to a text editor. (Notepad.exe will do fine). We will use it to carry out an execution test on our Lambda.
We must now define our target; clicking on the dropdown box, we will be presented with many services. Choose Lambda function.
The second dropdown box will display the Lambda functions we have created. Choose the Lambda we want to execute daily.
Click Configure details towards the bottom of the screen. The last step will be to name our Event Rule and add an optional description.
Testing the Lambda and viewing CloudWatch logs
Now that we have configured our daily billing alert, we need to perform a test and check the CloudWatch logs to make sure everything has worked as expected.Navigate back to the Lambda function we created at the start. To the left of the Test button, click on the up arrow. Then, click Configure test events.
Configuring our Lambda test event

Take the sample event we previously copied into a text editor. Copy this again, and paste it over the existing test so that it looks as below. Choose an Event name, and click Create.

Creating our Lambda test
Click on Test to execute our Lambda. All going well, we should see, at the top, of the screen a green successful message!
Successful execution of Lambda function

We can expand the details tab, but let’s look at CloudWatch logs to see the details.From the CloudWatch page, under Logs, click Log Groups. The prefix of /aws/lambda/ will be displayed, followed by the name of your Lambda function.
CloudWatch Billing alert log group

 Select the log group and the top log on the next page. The full process of the Lambda execution will be displayed in the log.
CloudWatch log group Lambda info

 Should you exceed your daily limit, you will receive an email notification that will look similar to this.
E mail notification sent from AWS SNS

# Summary
We have been through some exciting features in this article. We started by looking at the AWS new and improved CloudWatch user interface. Then, we went through the process of setting up a Lambda function, which used an SNS to send a notification and used CloudWatch to invoke a daily schedule of the Lambda function.CloudWatch has been used in many instances of this configuration, with the addition of locating metric information and viewing the invoked Lambda function logs. When the schedule runs daily, this will be the place to check should there be any issues.
