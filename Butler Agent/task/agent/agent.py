import dotenv
import os
from openai import OpenAI
from typing import Union
import json

dotenv.load_dotenv()

# Tools registry in the OpenAI function calling format
TOOLS_REGISTRY = [
    {
        "type": "function",
        "name": "check_weather",
        "description": "Check the current weather outside. Returns a short description of the weather conditions.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_wardrobe_items",
        "description": "List all clothing items in the wardrobe together with their status (clean or dirty).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "wash_clothing",
        "description": "Wash a dirty clothing item to make it clean. Returns an error if the item is not in the wardrobe.",
        "parameters": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Name of the clothing item to wash, exactly as listed in the wardrobe"
                }
            },
            "required": ["item_name"]
        }
    }
]

def check_weather() -> str:
    return "Cold, rainy"

WARDROBE = {
    "blue sweater": "dirty",
    "brown jacket": "dirty"
}

def get_wardrobe_items() -> str:
    # Formatted string with all wardrobe items and their status
    return "; ".join(f"Item {name} is {status}" for name, status in WARDROBE.items())

def wash_clothing(item_name) -> str:
    # Check if item exists, if yes - change status to clean, if no - return error
    if item_name not in WARDROBE:
        return f"Item '{item_name}' not found in wardrobe"
    WARDROBE[item_name] = "clean"
    return f"{item_name} is washed"

# Mapping from tool names to their implementations
TOOL_NAME_TO_FUNC = {
    "check_weather": check_weather,
    "get_wardrobe_items": get_wardrobe_items,
    "wash_clothing": wash_clothing,
}

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY") or os.getenv("LITELLM_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("LITELLM_BASE_URL"),
)

SYSTEM_PROMPT = """
You are a helpful assistant, your goal is to help user.
You have an access to the wardrobe and weather through tools, you can also clean dirty items.
Don't ask for permission to do the task, just do everything you can to help user.
"""

MAX_ITERATIONS = 5
MODEL_NAME = "gpt-4o-mini"

def run_agent_loop(context) -> Union[str, list[dict]]:
    iteration_number = 0
    while iteration_number < MAX_ITERATIONS:
        # THINK: LLM decides what to do next
        response = client.responses.create(
            model=MODEL_NAME,
            instructions=SYSTEM_PROMPT,
            input=context,
            tools=TOOLS_REGISTRY,
        )
        item_names = [type(item).__name__ for item in response.output]
        print(f'[THINK]: Model decided to return these items: {item_names}')

        # In real life, model can produce more than just one function call
        context += response.output

        # Check if LLM wants to use a tool
        for item in response.output:
            if item.type == "function_call":
                # ACT: execute the tool
                tool_result = TOOL_NAME_TO_FUNC[item.name](**json.loads(item.arguments))
                print(f'[ACT]: Calling "{item.name}" with arguments {item.arguments}')

                # OBSERVE: Add result to history
                context.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": tool_result,
                })
                print(f'[OBSERVE]: Result {tool_result}')
            if item.type == "message":
                # END: end the loop and return final response
                return item.content[0].text, context
        iteration_number += 1

    return "Agent didn't finish in time", context

def main():
    # Initialize conversation history
    context = []

    # Enter the conversation loop
    while True:
        input_message = input("[USER]: ").strip()
        if input_message.lower() in ["q", "quit", "exit"]:
            return
        context.append({"role": "user", "content": input_message})

        # Enter the agent loop
        print("[ENTERING AGENT LOOP]")
        response, context = run_agent_loop(context)
        print("[EXITING AGENT LOOP]")
        print(f"[ASSISTANT]: {response}")

if __name__ == "__main__":
    main()
