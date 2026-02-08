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
            def add_task_tool(title: str, description: str = None, priority: str = None, due_date: str = None, tags: str = None, recurrence: str = None) -> dict:
                """
                Create a new task.
                - title: Task title (REQUIRED)
                - description: Optional details
                - priority: 'HIGH', 'MEDIUM', or 'LOW'
                - due_date: ISO 8601 date string (e.g., '2023-12-31T23:59:00')
                - tags: Comma-separated tags (e.g., 'work,urgent')
                - recurrence: Recurrence rule (e.g., 'daily', 'weekly', or RRULE string)
                """
                if not title or len(title.strip()) < 1:
                    return {"error": "A non-empty title is required."}
                
                # Parse tags
                tag_list = [t.strip() for t in tags.split(',')] if tags else []
                
                # Parse priority
                parsed_priority = None
                if priority:
                    priority = priority.upper()
                    if priority in ['HIGH', 'MEDIUM', 'LOW']:
                        parsed_priority = priority
                
                # Parse recurrence (simple mapping)
                rrule = recurrence
                if recurrence:
                    recurrence = recurrence.lower()
                    if recurrence == 'daily': rrule = 'FREQ=DAILY'
                    elif recurrence == 'weekly': rrule = 'FREQ=WEEKLY'
                    elif recurrence == 'monthly': rrule = 'FREQ=MONTHLY'
                
                req = TaskCreateRequest(
                    title=title, 
                    description=description, 
                    user_id=user_id,
                    priority=parsed_priority,
                    due_date=due_date,
                    tags=tag_list,
                    recurrence_rule=rrule
                )
                res = add_task(req).model_dump()
                return {"status": "success", "task": res}

            @function_tool
            def list_tasks_tool(status: str = "all") -> dict:
                """List all tasks. status can be 'all', 'pending', or 'completed'."""
                req = TaskFilterRequest(user_id=user_id, status=status)
                res = list_tasks(req).model_dump()
                return res

            @function_tool
            def complete_task_tool(task_id: int, completed: bool = True) -> dict:
                """Mark a task as completed (true) or pending (false)."""
                res = complete_task(user_id, task_id, completed).model_dump()
                return {"status": "success", "task": res}

            @function_tool
            def delete_task_tool(task_id: int) -> dict:
                """Delete a task by ID."""
                res = delete_task(user_id, task_id)
                return res

            @function_tool
            def update_task_tool(task_id: int, title: str = None, description: str = None, completed: bool = None, priority: str = None, due_date: str = None, tags: str = None) -> dict:
                """Update an existing task."""
                # Parse tags
                tag_list = [t.strip() for t in tags.split(',')] if tags else None
                
                # Parse priority
                parsed_priority = None
                if priority:
                    priority = priority.upper()
                    if priority in ['HIGH', 'MEDIUM', 'LOW']:
                        parsed_priority = priority

                req = TaskUpdateRequest(
                    title=title, 
                    description=description, 
                    completed=completed,
                    priority=parsed_priority,
                    due_date=due_date,
                    tags=tag_list
                )
                res = update_task(user_id, task_id, req).model_dump()
                return {"status": "success", "task": res}

            # --- Agent Definition ---

            agent = Agent(
                name="FlowTask AI",
                instructions=f"""You are a highly capable Task Management AI. You are helping User ID: {user_id}.
                
                CAPABILITIES:
                - You can set PRIORITY (High, Medium, Low).
                - You can set DUE DATES (ask for specific dates/times). If user says "tomorrow", calculate the date.
                - You can add TAGS (e.g., work, personal).
                - You can set RECURRENCE (daily, weekly).

                CRITICAL RULE FOR TOOL USE:
                - Calling tools is your PRIMARY way of helping.
                - If the user implies an action ("I need to workout", "Call mom"), create a task immediately.
                - If the user mentions urgency ("urgent", "support", "critical"), set Priority to HIGH.
                - If the user mentions a time ("tomorrow", "at 5pm"), set the Due Date.

                CORE PRINCIPLES:
                1. **Autonomy**: Use `list_tasks_tool` to find task IDs if needed.
                2. **Inference**: User: "Buy milk urgent" -> Title: "Buy milk", Priority: HIGH.
                3. **Tags**: User: "coding task" -> Tags: "coding".

                Always confirm what you did: "I've added 'Buy milk' with High priority." """,
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