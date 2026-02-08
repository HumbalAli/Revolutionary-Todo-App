"""Dapr state management service for conversation context.

This module provides state management functionality using Dapr's
state store component for persisting conversation context.
"""

import logging
from typing import Any, Dict, Optional, List
from uuid import UUID
from datetime import datetime

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConversationContext(BaseModel):
    """Conversation state for AI assistant interactions."""
    user_id: UUID
    session_id: UUID
    last_activity: datetime
    context: Dict[str, Any] = {}


class FilterState(BaseModel):
    """Active filter state for task list."""
    priority: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[List[str]] = None


class DaprStateService:
    """Dapr state management service.

    This service manages application state using Dapr's state store,
    including conversation context for the AI assistant.

    Attributes:
        state_store_name: Name of the Dapr state store component
        dapr_port: Dapr sidecar HTTP port
    """

    def __init__(
        self,
        state_store_name: str = "statestore",
        dapr_port: int = 3500
    ):
        """Initialize state service.

        Args:
            state_store_name: Name of the Dapr state store component
            dapr_port: Dapr sidecar HTTP port
        """
        self.state_store_name = state_store_name
        self.dapr_port = dapr_port
        self.base_url = f"http://localhost:{dapr_port}/v1.0/state/{state_store_name}"

    async def save_state(
        self,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """Save state to Dapr state store.

        Args:
            key: State key
            value: State value (will be JSON serialized)
            metadata: Optional metadata (e.g., TTL)

        Returns:
            True if save succeeded
        """
        try:
            state_item = {
                "key": key,
                "value": value
            }
            if metadata:
                state_item["metadata"] = metadata

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=[state_item],
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code in (200, 204):
                    logger.debug(f"Saved state for key: {key}")
                    return True
                else:
                    logger.error(f"Failed to save state: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error saving state: {e}")
            return False

    async def get_state(self, key: str) -> Optional[Any]:
        """Get state from Dapr state store.

        Args:
            key: State key

        Returns:
            State value or None if not found
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/{key}")

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 204:
                    return None
                else:
                    logger.error(f"Failed to get state: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Error getting state: {e}")
            return None

    async def delete_state(self, key: str) -> bool:
        """Delete state from Dapr state store.

        Args:
            key: State key

        Returns:
            True if delete succeeded
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"{self.base_url}/{key}")

                if response.status_code in (200, 204):
                    logger.debug(f"Deleted state for key: {key}")
                    return True
                else:
                    logger.error(f"Failed to delete state: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error deleting state: {e}")
            return False

    async def save_conversation_context(
        self,
        user_id: UUID,
        session_id: UUID,
        context: ConversationContext,
        ttl_seconds: int = 3600
    ) -> bool:
        """Save conversation context with TTL.

        Args:
            user_id: User ID
            session_id: Session ID
            context: Conversation context to save
            ttl_seconds: Time to live in seconds (default 1 hour)

        Returns:
            True if save succeeded
        """
        key = f"conversation-state:{user_id}:{session_id}"
        metadata = {"ttlInSeconds": str(ttl_seconds)}

        return await self.save_state(
            key,
            context.model_dump(mode='json'),
            metadata
        )

    async def get_conversation_context(
        self,
        user_id: UUID,
        session_id: UUID
    ) -> Optional[ConversationContext]:
        """Get conversation context.

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            ConversationContext or None if not found
        """
        key = f"conversation-state:{user_id}:{session_id}"
        data = await self.get_state(key)

        if data:
            return ConversationContext(**data)
        return None

    async def update_conversation_context(
        self,
        user_id: UUID,
        session_id: UUID,
        updates: Dict[str, Any],
        ttl_seconds: int = 3600
    ) -> bool:
        """Update existing conversation context.

        Args:
            user_id: User ID
            session_id: Session ID
            updates: Fields to update
            ttl_seconds: Time to live in seconds

        Returns:
            True if update succeeded
        """
        existing = await self.get_conversation_context(user_id, session_id)

        if existing:
            # Merge updates into existing context
            existing_dict = existing.model_dump()
            existing_dict["context"].update(updates.get("context", {}))
            existing_dict["last_activity"] = datetime.utcnow()

            context = ConversationContext(**existing_dict)
        else:
            # Create new context
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                last_activity=datetime.utcnow(),
                context=updates.get("context", {})
            )

        return await self.save_conversation_context(
            user_id, session_id, context, ttl_seconds
        )

    async def save_filter_state(
        self,
        user_id: UUID,
        filters: FilterState
    ) -> bool:
        """Save user's active filter state.

        Args:
            user_id: User ID
            filters: Active filters

        Returns:
            True if save succeeded
        """
        key = f"filter-state:{user_id}"
        return await self.save_state(key, filters.model_dump())

    async def get_filter_state(self, user_id: UUID) -> Optional[FilterState]:
        """Get user's active filter state.

        Args:
            user_id: User ID

        Returns:
            FilterState or None if not found
        """
        key = f"filter-state:{user_id}"
        data = await self.get_state(key)

        if data:
            return FilterState(**data)
        return None


# Global state service instance
state_service = DaprStateService()


def get_state_service() -> DaprStateService:
    """Get the global Dapr state service instance.

    Returns:
        DaprStateService instance
    """
    return state_service
