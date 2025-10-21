import json
import display_functions
import os
import aisuite as ai
from openai import OpenAI

#  ===== Setting up models ====


from datetime import datetime


def get_current_time():
    """ 
    Returns the current time as a string.
    """
    return datetime.now().strftime("%H:%M:%S")



client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

tools = [{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Returns the current time as a string",
        "parameters": {}
    }
}]

def get_response(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=[
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ],
        tools = tools, # Your list of tools 
        # max_turns=5 
    )

    message = completion.choices[0].message
    print(message)
    if hasattr(message, "tool_calls") and message.tool_calls: 
        for tool_call in message.tool_calls:
            if tool_call.function.name == "get_current_time":
                result = get_current_time()
                print(f"🕒 Current time: {result}")
                return result 
    # otherwise, return the assistant message content 
    print(message.content) 
    return message.content


    # print(json.dumps(completion.model_dump(), indent=2, default=str))



if __name__ == "__main__":
    get_response("What time is it ?")

# ------ Create the first tool ---------



# print(get_current_time())

# ==== Creating the tool manually ===


