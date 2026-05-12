from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    # 1. Initialize the MCP Client (Do this OUTSIDE the loop to avoid reconnecting every time)
    client = MultiServerMCPClient(
        {
            "docker-mcp" : {
                "transport": "stdio",
                "command":"python",
                "args": ["mcp-server.py"]
            }
        }
    )
    
    # Get the tools from the MCP server
    tools = await client.get_tools()

    # LLM
    llm = ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.7
    )

    # Create Agent
    agent = create_agent(
        llm,
        tools
    )

    # Chat history
    chat_history = []

    print("--- Agent Ready! Type 'exit' or 'quit' to stop ---")

    while True:
        # Get input from the user
        user_input = input("\nUser: ")

        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        if not user_input.strip():
            continue

        # Add user message to history
        chat_history.append({"role": "user", "content": user_input})

        try:
            # 5. Invoke the agent with the full history
            response = await agent.ainvoke(
                {"messages": chat_history}
            )

            # Extract the last message from the agent's response
            agent_message = response['messages'][-1]
            
            # Print the response
            print(f"\nAgent: {agent_message.content}")

            # Add the agent's response to history so it remembers for the next turn
            chat_history.append(agent_message)

        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession ended by user.")