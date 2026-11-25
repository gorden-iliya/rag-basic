"""Console assistant over the NovaOps employee handbook (Bedrock converse + FAISS tool)."""
from bedrock_client import converse
from tools import handbook

MAX_ITERATIONS = 5

NOT_SET_UP_MSG = (
    "Error: the data for answering NovaOps employee handbook questions has not been set up yet. "
    "Run `python rag_data_populate.py first`"
)
NOT_FOUND_MSG = "Sorry, the data for answering this question was not found in the NovaOps employee handbook."

SYSTEM_PROMPT = f"""You are a helpful assistant for NovaOps employees.

- For ANY question about NovaOps (the company, its policies, benefits, time off, titles, career,
  rituals, devices, internal systems, severance, etc.) you MUST call the `handbook` tool. Never
  answer NovaOps questions from your own knowledge, and never decide a NovaOps question is
  "not covered" without searching first — even if it sounds unusual.
- For chit-chat or questions unrelated to NovaOps, answer directly and do NOT call the tool.
- The tool returns the top {handbook.TOP_K} passages, each with its source file and a cosine similarity
  score (higher = closer match). Judge relevance from BOTH the score and the passage content: a
  passage only counts if it actually answers the question, regardless of its score.
- If the passages don't answer the question, you may call the tool again with a better, rephrased
  query (different keywords, more specific or more general). You have at most {MAX_ITERATIONS - 1} searches.
- Answer NovaOps questions ONLY from relevant passages, and cite the source file names you used.
- If after searching no passage answers the question, reply exactly: "{NOT_FOUND_MSG}"
"""

TOOL_CONFIG = {"tools": [handbook.TOOL_SPEC]}
# Tool name -> search function; the tool name doubles as the index name under data/
TOOLS = {"handbook": handbook.search}

class ShortCircuit(Exception):
    """Ends the turn with a fixed reply instead of continuing the agent loop."""

def run_tool(name, tool_input):
    if name not in TOOLS:
        return f"Unknown tool: {name}"
    try:
        results = TOOLS[name](name, tool_input["query"])
    except handbook.DataNotReadyError:
        raise ShortCircuit(NOT_SET_UP_MSG)
    return handbook.format_results(results)

def answer(history, question):
    """Run the agent loop for one question; mutates history and returns the reply text."""
    turn_start = len(history)
    history.append({"role": "user", "content": [{"text": question}]})

    try:
        for _ in range(MAX_ITERATIONS):
            response = converse(history, SYSTEM_PROMPT, TOOL_CONFIG)
            message = response["output"]["message"]
            history.append(message)

            if response["stopReason"] != "tool_use":
                return " ".join(block.get("text", "") for block in message["content"]).strip()

            tool_results = []
            for block in message["content"]:
                if "toolUse" not in block:
                    continue
                use = block["toolUse"]
                text = run_tool(use["name"], use["input"])
                tool_results.append({
                    "toolResult": {
                        "toolUseId": use["toolUseId"],
                        "content": [{"text": text or "No passages returned."}]
                    }
                })
            history.append({"role": "user", "content": tool_results})

        raise ShortCircuit(NOT_FOUND_MSG)
    except ShortCircuit as stop:
        reply = str(stop)
    except Exception:
        del history[turn_start:]
        raise

    # Drop the unfinished tool exchange: Converse rejects a toolUse without a matching toolResult 
    del history[turn_start:]
    # add the NOT_FOUND_MSG (reply) from line 73 to the assistant content
    history.append({"role": "user", "content": [{"text": question}]})
    history.append({"role": "assistant", "content": [{"text": reply}]})
    return reply

def main():
    print("NovaOps handbook assistant. Type 'exit' or 'quit' to leave.")
    history = []

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "bye", "q"}:
            break
        try:
            print(f"Assistant: {answer(history, question)}\n")
        except Exception as exc:
            print(f"Assistant: [error] {exc}\n")
    print("Goodbye!")

if __name__ == "__main__":
    main()