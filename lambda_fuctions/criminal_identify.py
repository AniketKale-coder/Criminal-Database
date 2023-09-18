import json
import logging

import boto3

AWS_REGION = 'us-east-1'

def initialize_clients():
    rekognition = boto3.client('rekognition', region_name=AWS_REGION)
    dynamodb_client = boto3.resource('dynamodb', region_name=AWS_REGION)
    s3 = boto3.client('s3', region_name=AWS_REGION)
    return rekognition, dynamodb_client, s3

def identify_face(image_bytes, rekognition, dynamodb_client):
    try:
        criminal_Table = dynamodb_client.Table("CriminalData")

        response = rekognition.search_faces_by_image(
            CollectionId='Criminals',
            Image={'Bytes': image_bytes}
        )

        for face_match in response['FaceMatches']:
            face_id = face_match['Face']['FaceId']
            face = criminal_Table.get_item(
                Key={'rekognitionId': face_id}
            )

            if 'Item' in face:
                return build_response(200, {
                    "message": "success",
                    "data": {
                        "personName": face["Item"]["firstName"]
                    }
                })

        return build_response(404, {"message": "Person Not Found"})
    except Exception as e:
        logging.error(f"Error in identify_face: {str(e)}")
        return build_response(500, {"message": "Internal Server Error"})

def build_response(status_code, body=None):
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response

def lambda_handler(event, context):
    rekognition, dynamodb_client, s3 = initialize_clients()

    try:
        target_file = event['target_file']
        image_bytes = s3.get_object(Bucket="suspectesimages", Key=target_file)['Body'].read()

        face_matches = identify_face(image_bytes, rekognition, dynamodb_client)
        logging.info(f"Face matches: {face_matches}")

        return face_matches
    except Exception as e:
        logging.error(f"Error in lambda_handler: {str(e)}")
        return build_response(500, {"message": "Internal Server Error"})
    

