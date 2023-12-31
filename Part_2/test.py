from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import pinecone
import numpy as np
import pinecone
import boto3
from botocore.exceptions import NoCredentialsError
import os
from PIL import Image

app = FastAPI()

pinecone_api_key = "878f92d2-ce36-4be5-bbc0-05a56ff092fc"
index_name = "adm4"
s3_bucket_name = "assignment4admt5"

pinecone.init(api_key=pinecone_api_key, environment="gcp-starter")
index = pinecone.Index(index_name)

s3_resource = boto3.resource('s3',
                             region_name='us-east-2',
                             aws_access_key_id='AKIAQ4WOK7VQVKP4WJVB',
                             aws_secret_access_key='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')

class ImageSearchRequest(BaseModel):
    image: List[float]

@app.post("/image_search")
async def image_search(request: ImageSearchRequest):
    image_vector = request.image

    closest_image_ids = index.query(
        vector=image_vector,
        top_k=4,
        include_values=False
    )

    closest_image_ids = [i['id'] for i in closest_image_ids['matches']]

    images_from_s3 = []

    for image_id in closest_image_ids:
        try:
            image_object = s3_resource.Object(s3_bucket_name, f"new_dataset_assignment_5/new_dataset/{image_id}")
            images_from_s3.append(image_object.get()['Body'].read())
        except NoCredentialsError:
            return HTTPException(status_code=500, detail="AWS credentials not available.")
        except Exception as e:
            return HTTPException(status_code=500, detail=f"Error retrieving image {image_id}: {str(e)}")

    return closest_image_ids
