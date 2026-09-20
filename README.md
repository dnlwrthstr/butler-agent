# Butler Agent

A small autonomous AI assistant built with the OpenAI Responses API. It implements the
THINK → ACT → OBSERVE agent loop: the model decides which tools to call, the tools are
executed, their results are fed back into the conversation, and the loop continues until
the model produces a final answer.

Built as a [Hyperskill](https://hyperskill.org) study project.

## Tools

| Tool | Description |
|------|-------------|
| `check_weather()` | Returns the current weather (stubbed as `Cold, rainy`) |
| `get_wardrobe_items()` | Lists every item in the wardrobe with its clean/dirty status |
| `wash_clothing(item_name)` | Washes a dirty item; returns an error if the item does not exist |

State (the `WARDROBE` dict) persists across tool calls and conversation turns.

## Example

```
[USER]: What should I wear today?
[ENTERING AGENT LOOP]
[THINK]: Model decided to return these items: ['ResponseFunctionToolCall', 'ResponseFunctionToolCall']
[ACT]: Calling "check_weather" with arguments {}
[OBSERVE]: Result Cold, rainy
[ACT]: Calling "get_wardrobe_items" with arguments {}
[OBSERVE]: Result Item blue sweater is dirty; Item brown jacket is dirty
[THINK]: Model decided to return these items: ['ResponseFunctionToolCall', 'ResponseFunctionToolCall']
[ACT]: Calling "wash_clothing" with arguments {"item_name":"blue sweater"}
[OBSERVE]: Result blue sweater is washed
[ACT]: Calling "wash_clothing" with arguments {"item_name":"brown jacket"}
[OBSERVE]: Result brown jacket is washed
[THINK]: Model decided to return these items: ['ResponseOutputMessage']
[EXITING AGENT LOOP]
[ASSISTANT]: Today's weather is cold and rainy. I've washed your blue sweater and brown jacket...
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your OPENAI_API_KEY
```

## Run

```bash
cd "Butler Agent/task/agent"
python agent.py
```

Type `q`, `quit` or `exit` to end the conversation.

## Tests

```bash
cd "Butler Agent/task"
python tests.py
```
