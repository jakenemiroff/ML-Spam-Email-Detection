# ML Spam Email Detection

In this project, I developed a spam detection system built on AWS.

Upon receipt of an email, the application either classifies the message as spam or a valid message.

This is based on the prediction obtained from an spam filter machine learning model created using Amazon SageMaker.

Whenever an email is received, a Lambda function triggers the SageMaker endpoint to classify the email. 

Afterwards, Lmabda invokes SES in order to reply to the sender with the results.

The definition and provision of the resources on AWS cloud is done through the AWS Cloudformation template.

AWS services used:

  - Amazon SageMaker
  - AWS SES
  - Lambda
  - S3
  - CloudFormation

### Please note that the notebook is not my own code. I used it in order to further my knowledge of deep learning and using AWS SageMaker. I am including it in case someone else comes across it and wants to learn from it as I have done.
