import boto3
from langchain_aws import ChatBedrock

bedrock         = boto3.client("bedrock")

def get_claude3_models():
    claude3_models = []
    models = bedrock.list_foundation_models(byProvider='Anthropic',byOutputModality= "TEXT", byInferenceType='ON_DEMAND').get("modelSummaries")
    for m in models:
        if 'IMAGE' in m.get("inputModalities"):
            claude3_models.append(m.get("modelId"))    
    
    return claude3_models


def get_chat_model(level):
    models_id = get_claude3_models()
    models_id = ['anthropic.claude-3-sonnet-20240229-v1:0', 'anthropic.claude-3-haiku-20240307-v1:0', 'anthropic.claude-3-opus-20240229-v1:0']

    model_fast = 'anthropic.claude-3-haiku-20240307-v1:0'
    model_smart = 'anthropic.claude-3-opus-20240229-v1:0'
    model_normal = 'anthropic.claude-3-sonnet-20240229-v1:0'

    print(models_id)
    if level == "fast":
        chat = ChatBedrock(model_id=model_fast,model_kwargs={"temperature": 0})
    elif level == "normal":
        chat = ChatBedrock(model_id=model_normal, model_kwargs={"temperature": 0})
    elif level == "smart":
        chat = ChatBedrock(model_id=model_smart, model_kwargs={"temperature": 0})

    return chat