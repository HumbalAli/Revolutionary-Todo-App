"""
AI Task Agent using OpenAI Agents SDK
This module implements an AI agent that can manage tasks through natural language
"""

from openai import AsyncOpenAI
from ..api.mcp_tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskFilterRequest
)
import os
import json

class TaskManagementAgent:
    def __init__(self):
        # Initialize Groq client
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            # Check for OPENAI_API_KEY as fallback
            self.groq_api_key = os.getenv("OPENAI_API_KEY")
            if not self.groq_api_key:
                # For development, use a dummy key if neither is set
                print("WARNING: GROQ_API_KEY or OPENAI_API_KEY environment variable is required for production use.")
                self.groq_api_key = "dummy-key-for-development"

        # Use base URL for Groq if it's a Groq key, otherwise use OpenAI default
        # Strip potential quotes/spaces from the key
        if self.groq_api_key:
            self.groq_api_key = self.groq_api_key.strip().strip('"').strip("'")
            
        base_url = "https://api.groq.com/openai/v1" if os.getenv("GROQ_API_KEY") else None

        # Use AsyncOpenAI for better async integration
        self.client = AsyncOpenAI(
            api_key=self.groq_api_key,
            base_url=base_url
        )

    async def chat(self, messages: list, user_id: int) -> dict:
        """
        Process a conversation with multiple messages using openai-agents SDK
        """
        # Normalize messages to dicts
        normalized_messages = []
        for msg in messages:
            m_dict = {}
            if isinstance(msg, dict):
                m_dict = msg
            elif hasattr(msg, "model_dump"):
                m_dict = msg.model_dump()
            elif hasattr(msg, "dict"):
                m_dict = msg.dict()
            
            if m_dict:
                # Ensure role and content exist
                role = m_dict.get("role", "user")
                # Normalize assistant role name if needed (some SDKs prefer 'assistant')
                if role == "ai": role = "assistant"
                normalized_messages.append({
                    "role": role,
                    "content": m_dict.get("content", m_dict.get("text", ""))
                })
        
        # Keep last 10 messages
        messages = normalized_messages[-10:]

        try:
            if self.groq_api_key == "dummy-key-for-development":
                return {"response": "(Dummy Mode) I see your messages.", "action_performed": None, "task_result": None}

            from agents import Agent, Runner, set_default_openai_client, function_tool, set_tracing_disabled

            set_tracing_disabled(True)
            set_default_openai_client(self.client)

            # --- Tool Definitions ---

            @function_tool
            def add_task_tool(title: str, description: str = None) -> dict:
                """Create a new task for the current user. title is REQUIRED."""
                if not title or len(title.strip()) < 1:
                    return {"error": "A non-empty title is required."}
                req = TaskCreateRequest(title=title, description=description, user_id=user_id)
                res = add_task(req).model_dump()
                return {"status": "success", "task": res}

            @function_tool
            def list_tasks_tool(status: str = "all") -> dict:
                """List all tasks for the current user. Use this to find task IDs before updating or deleting."""
                req = TaskFilterRequest(user_id=user_id, status=status)
                res = list_tasks(req).model_dump()
                return res

            @function_tool
            def complete_task_tool(task_id: int, completed: bool = True) -> dict:
                """Set a task's completion status by ID."""
                res = complete_task(user_id, task_id, completed).model_dump()
                return {"status": "success", "task": res}

            @function_tool
            def delete_task_tool(task_id: int) -> dict:
                """Delete a task by ID. List tasks first to get the correct ID."""
                res = delete_task(user_id, task_id)
                return res

            @function_tool
            def update_task_tool(task_id: int, title: str = None, description: str = None, completed: bool = None) -> dict:
                """Update task properties by ID."""
                req = TaskUpdateRequest(title=title, description=description, completed=completed)
                res = update_task(user_id, task_id, req).model_dump()
                return {"status": "success", "task": res}

            # --- Agent Definition ---

            agent = Agent(
                name="FlowTask AI",
                instructions=f"""You are a highly capable Task Management AI. You are helping User ID: {user_id}.
                
                CRITICAL RULE FOR TOOL USE:
                - If you decide to call a tool, you MUST NOT include any conversational text, explanations, or preamble before the tool call.
                - Your response should consist ONLY of the tool call if you are performing an action.
                - Do NOT explain why you are calling a tool. Just call it.
                
                CORE PRINCIPLES:
                1. **Autonomy**: If a user asks to delete or update tasks but doesn't provide IDs, IMMEDIATELY use `list_tasks_tool` to find them yourself. Don't ask the user for info you can get via tools.
                2. **Context Awareness**: Look at the conversation history. If the user previously gave a title, use it.
                3. **Decisiveness**: If the user says "exercise" after you asked for a title, infer that "exercise" IS the title.
                4. **Proactive help**: When listing tasks for deletion, show them to the user and ask for confirmation OR execute if the command was specific (e.g., "remove all tasks except X").
                
                SCENARIOS:
                - User: "Delete my old tasks" -> Action: List tasks, identify non-Exercise tasks, then call delete for each.
                - User: "Add task" -> AI: "What's the title?" -> User: "Gym" -> AI: Add task with title "Gym".
                
                Always confirm your actions clearly after the tool has executed.""",
                model="llama-3.3-70b-versatile",
                tools=[add_task_tool, list_tasks_tool, complete_task_tool, delete_task_tool, update_task_tool]
            )

            # Run with full conversation context
            result = await Runner.run(agent, input=messages)
            
            final_text = str(result.final_output) if hasattr(result, 'final_output') else str(result)
            
            return {
                "response": final_text,
                "action_performed": "agent_action",
                "task_result": None
            }

        except Exception as e:
            # Fallback debug
            import traceback
            traceback.print_exc()
            return {
                "response": f"Error using Agents SDK: {str(e)}",
                "action_performed": None,
                "task_result": None
            }