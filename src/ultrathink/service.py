import os
from .thought import Thought
from .session import ThinkingSession
from .dto import ThoughtRequest, ThoughtResponse


class UltraThinkService:
    """
    Application Service: Orchestrates the sequential thinking process
    Handles session lifecycle and translates between interface DTOs and domain entities
    """

    def __init__(self) -> None:
        disable_logging = (
            os.environ.get("DISABLE_THOUGHT_LOGGING", "").lower() == "true"
        )
        self._session = ThinkingSession(disable_logging=disable_logging)

    def process_thought(self, request: ThoughtRequest) -> ThoughtResponse:
        """
        Process a thought request (Application Service orchestration)

        Args:
            request: ThoughtRequest DTO from interface layer

        Returns:
            ThoughtResponse DTO for interface layer

        Raises:
            ValidationError: If request validation fails
            ValueError: If domain validation fails
        """
        # 1. Translate DTO to domain entity
        thought = Thought(**request.model_dump())

        # 2. Execute domain logic
        self._session.add_thought(thought)

        # 3. Translate domain result to response DTO
        return ThoughtResponse(
            thought_number=thought.thought_number,
            total_thoughts=thought.total_thoughts,
            next_thought_needed=thought.next_thought_needed,
            branches=self._session.branch_ids,
            thought_history_length=self._session.thought_count,
        )
