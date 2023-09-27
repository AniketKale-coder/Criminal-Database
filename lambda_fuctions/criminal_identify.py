import json
import logging

import boto3

AWS_REGION = 'us-east-1'

s3 = boto3.client('s3', region_name=AWS_REGION)
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
rekognition_client = boto3.client('rekognition',region_name=AWS_REGION)
dynamodb_client = boto3.resource('dynamodb',region_name=AWS_REGION)
bucket_name='suspectesimages'
criminal_table = dynamodb_client.Table("CriminalData")



def lambda_handler(event, context): 
    print(event)
    objectKey = event ['queryStringParameters']['objectKey'] 
    image_bytes = s3.get_object(Bucket=bucket_name,Key=objectKey) ['Body'].read() 
    response = rekognition_client.search_faces_by_image(
    CollectionId='employees', Image={'Bytes': image_bytes})

    for match in response['FaceMatches']: 
        print(match['Face']['FaceId'], match ['Face']['Confidence'])
        face = criminal_table.get_item(
        Key={
        'rekognitionId': match['Face']['FaceId']
        }
    )
    if 'Item' in face:
        print('Person Found: ', face['Item'])
        return buildResponse(200, { 
        'Message': 'Success',
        'firstName': face['Item']['firstName'],
        'lastName': face['Item']['lastName'],
        'criminal_id': face['Item']['criminal_id'],
        'date_of_birth': face['Item']['date_of_birth'],
        'years_active': face['Item']['years_active'],
        'criminal_charges_list': face['Item']['criminal_charges_list'],
        'nick_name': face['Item']['nick_name']
        })
    print('Person could not be recognized.') 
    return buildResponse(403, {'Message': 'Person Not Found'})

def buildResponse(statusCode, body=None): 
    response = {
    'statusCode': statusCode,
    'headers': {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'}
    }
    if body is not None:
        response['body'] = json.dumps (body)
    return response

