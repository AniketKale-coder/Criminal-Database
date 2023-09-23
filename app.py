import json
import os
import uuid

import boto3
from flask import Flask, redirect, render_template, request, url_for
from pyparsing import Literal

app = Flask(__name__)

AWS_SECRET_ACCESS_ID = os.environ.get('ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('KEY')
AWS_REGION = 'us-east-1'
CRIMINAL_BUCKET = 'criminaldbimages'
SUSPECTS_BUCKET = 'suspectesimages'
TRG_IMG = 'target_file'  # Specify the folder within the bucket

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_SECRET_ACCESS_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name=AWS_REGION)

lambda_client = boto3.client('lambda',
                             aws_access_key_id=AWS_SECRET_ACCESS_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             region_name=AWS_REGION)

rekognition_client = boto3.client('rekognition',
                                  aws_access_key_id=AWS_SECRET_ACCESS_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  region_name=AWS_REGION)

dynamodb_client = boto3.resource('dynamodb',
                                 aws_access_key_id=AWS_SECRET_ACCESS_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                 region_name=AWS_REGION)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registration.html')
def registration():
    return render_template('registration.html')




@app.route('/registration', methods=['POST'])
def registre():
    image = request.files['image']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    nick_name = request.form['nick_name']
    date_of_birth = request.form['date_of_birth']
    years_active = request.form['years_active']
    criminal_charges_string = request.form['criminal_charges']
    criminal_charges_list = criminal_charges_string.split(",")

    # # Generate a unique ID for the criminal
    criminal_id = str(uuid.uuid4())

    # Upload image to S3

    s3.upload_fileobj(image, CRIMINAL_BUCKET, f"{criminal_id}.jpg")

    # Use Rekognition to generate Face ID
    response = rekognition_client.index_faces(
        CollectionId="Criminals",
        Image={
            'S3Object': {
                'Bucket': CRIMINAL_BUCKET,
                'Name': f"{criminal_id}.jpg"
            }
        }
    )
    face_id = response['FaceRecords'][0]['Face']['FaceId']

    # Store data in DynamoDB
    criminal_table = dynamodb_client.Table("CriminalData")
    criminal_table.put_item(Item={
        'CriminalId': criminal_id,
        'FirstName': first_name,
        'LastName': last_name,
        'DOB': date_of_birth,
        'YearsActive': years_active,
        'CriminalCharges': criminal_charges_list,
        'NickName': nick_name,
        'FaceId': face_id
    })

    return redirect(url_for('index'))


@app.route('/upload', methods=['POST'])
def upload():
    if 'image1' and 'image2' in request.files:
        image1 = request.files['image1']
        if image1.filename != '' and image1.filename != '':
            # Upload images to S3
            s3.upload_fileobj(image1, SUSPECTS_BUCKET, f'{image1.filename}')
            # Invoke Lambda function with image parameters
            lambda_payload = {
                'target_file': f'{image1.filename}',
            }
            lambda_response = lambda_client.invoke(
                FunctionName='faceComp',
                InvocationType='RequestResponse',  # Synchronous invocation
                Payload=json.dumps(lambda_payload)
            )

            # Retrieve Lambda function response
            response_payload = lambda_response['Payload'].read().decode(
                'utf-8')

            return f"Images uploaded successfully. lambda invoke{response_payload}"
    return "Failed to upload images."


if __name__ == '__main__':
    app = Flask(__name__, static_url_path='/static')
    app.run(debug=True, port=5000)

