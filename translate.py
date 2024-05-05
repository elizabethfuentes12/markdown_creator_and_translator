from langchain_core.messages import HumanMessage,SystemMessage, AIMessage
from langchain_aws import ChatBedrock


def get_suggestions(chat, content, language):
    system_prompt = f"""
    You are an expert translator into {language} who uses language in a neutral tone. Translate the following blog.
    You cannot translate the following:
    - AWS service names.
    - URLs or links.
    - Code. 
    You must return the content in the same format that is delivered to you. Just return the translated content without preamble afterword or closing."
    """
    messages = [SystemMessage(content=system_prompt)]

    messages.append(HumanMessage(content=[
        {"type":"text", "text": "This is the blog content:\n\n"}, 
        *content
        ]))


    ai_response = chat.invoke(messages)
    print(ai_response.response_metadata)
    return ai_response.content