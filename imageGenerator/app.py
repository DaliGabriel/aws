import boto3
import botocore.config
import json
from datetime import datetime

def startup_ideas_generator_using_bedrock(bussines_area:str)-> str:
    
    prompt=f"""
    <s>[INST]Human: Give me 20 startup software ideas that could be developed for a one person for a new business in the following business area: {bussines_area}
    Assistant:[/INST]
    """

    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
    }

    try:
        
        bedrock=boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(read_timeout=300,retries={'max_attempts':3})
            )
            
        response=bedrock.invoke_model(
            body=json.dumps(body),
            modelId="meta.llama2-70b-chat-v1"
            )

        response_content=response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        startup_details=response_data['generation']
        return startup_details
    except Exception as e:
        print(f"Error generating the startup ideas:{e}")
        return e

def save_startup_ideas_s3(s3_key,s3_bucket,generate_startup_ideas):
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body =generate_startup_ideas )
        print("Startup ideas saved to s3")

    except Exception as e:
        print("Error when saving the startup ideas to s3")
        

def lambda_handler(event, context):
    # TODO implement
    event=json.loads(event['body'])
    bussines_area=event['bussines_area']

    generate_startup_ideas=startup_ideas_generator_using_bedrock(bussines_area)

    if generate_startup_ideas:
        current_time=datetime.now().strftime('%H%M%S')
        s3_key=f"startup_ideas/{current_time}.txt"
        s3_bucket='your_bucket_name'
        save_startup_ideas_s3(s3_key,s3_bucket,generate_startup_ideas)
        
        print(generate_startup_ideas)
        return{
        'statusCode':200,
        'body':json.dumps(generate_startup_ideas)
        }

    else:
        print("No startup was generated")
        return{
        'statusCode':400,
        'body':json.dumps('Startup Generation is not completed')
        }


