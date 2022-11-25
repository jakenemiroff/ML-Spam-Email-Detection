import json
import urllib.parse
import boto3
import email
from sms_spam_classifier_utilities import one_hot_encode
from sms_spam_classifier_utilities import vectorize_sequences

def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    sagemaker_client = boto3.client('runtime.sagemaker')
    ses_client = boto3.client('ses', region_name='us-east-1')

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        body = response['Body'].read().decode('utf-8')
        
        # Extract contents from email
        contents = email.message_from_string(body)
        
        date = contents.get('Date')
        sender = contents.get('From')
        
        sender = sender[sender.find('<')+len('<'):sender.rfind('>')]
        
        recipient = contents.get('To')
        
        subject = contents.get('Subject')
        
        body = ''
        
        if contents.is_multipart():
            for payload in contents.get_payload():
                if payload.get_content_type() == 'text/plain':
                    body = payload.get_payload()
        else:
            body = contents.get_payload()
            
        body = body.replace("\r", " ").replace("\n", " ")
        
        # Prepare input for sagemaker endpoint
        endpoint_name = 'sms-spam-classifier-mxnet-2022-11-25-20-37-08-777'
        detector_input = [body]
        
        vocabulary_length = 9013
        one_hot_detector_input = one_hot_encode(detector_input, vocabulary_length)
        encoded_detector_input = vectorize_sequences(one_hot_detector_input, vocabulary_length)
        detector_input = json.dumps(encoded_detector_input.tolist())
        
        # Get a response from the sagemaker endpoint and decode it
        response = sagemaker_client.invoke_endpoint(EndpointName=endpoint_name, ContentType='application/json', Body=detector_input)
        
        results = response['Body'].read().decode('utf-8')
        results_json = json.loads("" + results + "")
        
        # Get the class and confidence percentage
        if(results_json['predicted_label'][0][0] == 1.0):
            
            spam_class = 'SPAM'
        
        else:
             spam_class = 'HAM'
        
        confidence_score = str(results_json['predicted_probability'][0][0]*100)
        confidence_score = confidence_score.split('.')[0]
        
        # Send the email through SES
        if len(body) > 240:
            body = body[:240]
        
        response_email = 'We received your email sent at ' + date + ' with the subject ' + subject + '.\n\n' + 'Here is a 240 character sample of the email body:\n' + body + '\n\n' + 'The email was categorized as ' + spam_class + ' with a ' + confidence_score + '% confidence.'
        
        charset = "UTF-8"
        response = ses_client.send_email(
            Destination={
                "ToAddresses": [
                    sender,
                ],
            },
            Message={
                "Body": {
                    "Text": {
                        "Charset": charset,
                        "Data": response_email,
                    }
                },
                "Subject": {
                    "Charset": charset,
                    "Data": "Spam Detector Results",
                },
            },
            Source=recipient,
        )
        
        return "success"
    
    except Exception as e:
        print(e)
        raise e