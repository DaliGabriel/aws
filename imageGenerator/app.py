import boto3
import json
from datetime import datetime
import base64

def images_generator_using_bedrock(image_description:str)-> str:
    
    prompt_data = f"""{image_description}"""
    
    prompt_template=[{"text":prompt_data,"weight":1}]
    
    payload = {
        "text_prompts":prompt_template,
        "cfg_scale": 10,
        "seed": 0,
        "steps":50,
        "width":512,
        "height":512
    }

    try:
        
        bedrock=boto3.client("bedrock-runtime")
        
        body = json.dumps(payload)
        
        model_id = "stability.stable-diffusion-xl-v1"
            
        response = bedrock.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
        )
          
        response_body = json.loads(response.get("body").read())
        artifact = response_body.get("artifacts")[0]
        image_encoded = artifact.get("base64").encode("utf-8")
        image_bytes = base64.b64decode(image_encoded)
        
        print('The response of the model was encoded to b64')
        
        return image_bytes
        
    except Exception as e:
        print(f"Error generating the startup ideas:{e}")
        return e

def save_image_to_s3(s3_key,s3_bucket,image_bytes: bytes):
    s3=boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body =image_bytes )
        print(f"Image saved to S3 with key: {s3_key}")

    except Exception as e:
        print(f"Error when saving the image to S3: {e}")
        

def lambda_handler(event, context):
    # TODO implement
    event=json.loads(event['body'])
    image_description=event['image_description']
    
    

    generate_image=images_generator_using_bedrock(image_description)
    
    

    if generate_image:
        current_time=datetime.now().strftime('%H%M%S')
        s3_key=f"images_generated/{current_time}.jpg"
        s3_bucket='testbucketdali'
        
        save_image_to_s3(s3_key,s3_bucket,generate_image)
        
        print('the image was saved into s3 bucket')
        
        return{
        'statusCode':200,
        'body': json.dumps({'s3_url': f'https://{s3_bucket}.s3.amazonaws.com/{s3_key}'})
        }

    else:
        print("No image was generated")
        return{
        'statusCode':400,
        'body':json.dumps('Image generatino is not completed')
        }


