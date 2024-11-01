from dotenv import load_dotenv, dotenv_values
from sagemaker import get_execution_role
import boto3
from typing import List

load_dotenv()

sm_client = boto3.client(service_name="sagemaker")
runtime_sm_client = boto3.client(service_name="sagemaker-runtime")

def query_endpoint(endpoint_name, query_json):
    query_json_formatted = json.dumps(query_json)
    response = runtime_sm_client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=query_json_formatted
    )
    return json.loads(response["Body"].read().decode("utf-8"))

query_ai_webservice = lambda query_json: query_endpoint(os.getenv("AI_WEBSERVICE_ENDPOINT"), query_json)

_query_ai_logo_vectorizer_service = lambda query_json : query_endpoint(os.getenv("LOGO_VECTORIZER_ENDPOINT"), query_json)

def _query_logo_vectorizer(query_json) :
    body = {
        "model_name": "logo_vectorizer_v1",
        "model_input":query_json
    }
    return _query_ai_logo_vectorizer_service(query_json=body)

def query_logo_vectorizer_image(imageb64:str):
    query_json = {
        "type":"images",
        "inputs":[imageb64]
    }
    return _query_logo_vectorizer(query_json=query_json)["image_features"][0]

def query_logo_vectorizer_text(text:str):
    query_json = {
        "type" : 'texts',
        "inputs":[text]
    }
    return _query_logo_vectorizer(query_json=query_json)["text_features"][0]

def query_rag_text_vectorizer(texts:List[str]):
    query_json = {
        "model_name":"rag_text_embedder",
        "model_input":{
            "texts" : texts
        }
    }
    return query_ai_webservice(query_json)
