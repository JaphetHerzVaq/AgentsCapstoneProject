
import os
import asyncio
import logging
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk.agents import Agent

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

async def test_multimodal_async():
    agent = Agent(
        name="TestAgent",
        model=Gemini(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY),
        instruction="You are a helpful assistant. Describe the document provided.",
    )

    # Initialize runner with app_name="agents" to match the warning/expectation
    runner = InMemoryRunner(agent=agent, app_name="agents")
    
    # Create session
    session_id = "test_session"
    user_id = "test_user"
    # Pass app_name to create_session
    await runner.session_service.create_session(
        session_id=session_id, 
        user_id=user_id,
        app_name="agents"
    )
    print(f"Created session {session_id}")

    # Load PDF
    pdf_path = "../resources/input/papers_to_review/document_safe_beliefs.pdf"
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    prompt_text = "Please describe this document."
    
    # Create Content object
    try:
        pdf_part = types.Part.from_bytes(data=pdf_data, mime_type="application/pdf")
        text_part = types.Part(text=prompt_text)
        content = types.Content(parts=[text_part, pdf_part], role="user")
        print("Created Content with types.Part.from_bytes")
    except Exception as e:
        print(f"Error creating content: {e}")
        return

    print("Running agent with multimodal prompt via run_async...")
    try:
        events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            events.append(event)
        
        print(f"Collected {len(events)} events.")
        
        # Extract text from response events
        for event in events:
             if (hasattr(event, 'actions') and
                    event.actions is not None and
                    hasattr(event.actions, 'state_delta') and
                    event.actions.state_delta is not None and
                    isinstance(event.actions.state_delta, dict)):
                 print("State Delta:", event.actions.state_delta)
                 
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_multimodal_async())
