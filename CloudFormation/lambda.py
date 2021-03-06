#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# or in the "license" file accompanying this file. This file is distributed 
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either 
# express or implied. See the License for the specific language governing 
# permissions and limitations under the License.

import json
import os
import boto3
import requests

def handler(event, context):
    try:
        operation = event['ResourceProperties']['Operation']

        if operation == 'CleanupSagemakerBucket':
            if event['RequestType'] == 'Delete':
                bucketName = os.environ['SAGEMAKER_BUCKET_NAME']
                s3 = boto3.resource('s3')
                bucket = s3.Bucket(bucketName)
                bucket.objects.filter(Prefix='battlesnake-aws/').delete()
                bucket.objects.filter(Prefix='battlesnake-mxnet/').delete()
        elif operation == 'CleanupSagemakerEndpoint':
            if event['RequestType'] == 'Delete':
                deployment_name = 'battlesnake-endpoint'
                client = boto3.client('sagemaker')
                response = client.describe_endpoint_config(EndpointConfigName=deployment_name)
                model_name = response['ProductionVariants'][0]['ModelName']
                client.delete_model(ModelName=model_name)    
                client.delete_endpoint(EndpointName=deployment_name)
                client.delete_endpoint_config(EndpointConfigName=deployment_name)

        sendResponseCfn(event, context, "SUCCESS")
    except Exception as e:
        print(e)
        sendResponseCfn(event, context, "FAILED")


def sendResponseCfn(event, context, responseStatus):
    response_body = {'Status': responseStatus,
                     'Reason': 'Log stream name: ' + context.log_stream_name,
                     'PhysicalResourceId': context.log_stream_name,
                     'StackId': event['StackId'],
                     'RequestId': event['RequestId'],
                     'LogicalResourceId': event['LogicalResourceId'],
                     'Data': json.loads("{}")}

    requests.put(event['ResponseURL'], data=json.dumps(response_body))
