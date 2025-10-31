import os
import uuid
from .thought import Thought
from .session import ThinkingSession
from .dto import ThoughtRequest, ThoughtResponse


class UltraThinkService:
    """
    Application Service: Orchestrates the sequential thinking process
    Handles session lifecycle and translates between interface DTOs and domain entities
    """

    def __init__(self) -> None:
        self._disable_logging = (
            os.environ.get("DISABLE_THOUGHT_LOGGING", "").lower() == "true"
        )
        self._sessions: dict[str, ThinkingSession] = {}

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
        # Get or create session (resilient pattern)
        if request.session_id is None:
            # Generate new session ID
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = ThinkingSession(
                disable_logging=self._disable_logging
            )
        else:
            # Use existing session or create new with provided ID
            session_id = request.session_id
            if session_id not in self._sessions:
                self._sessions[session_id] = ThinkingSession(
                    disable_logging=self._disable_logging
                )

        session = self._sessions[session_id]

        # Auto-assign thought_number if not provided
        if request.thought_number is None:
            thought_number = session.thought_count + 1
        else:
            thought_number = request.thought_number

        # 1. Translate DTO to domain entity (exclude session_id, override thought_number)
        thought_data = request.model_dump(exclude={"session_id"})
        thought_data["thought_number"] = thought_number
        thought = Thought(**thought_data)

        # 2. Execute domain logic
        session.add_thought(thought)

        # 3. Translate domain result to response DTO
        return ThoughtResponse(
            session_id=session_id,
            thought_number=thought.thought_number,
            total_thoughts=thought.total_thoughts,
            next_thought_needed=thought.next_thought_needed,
            branches=session.branch_ids,
            thought_history_length=session.thought_count,
            confidence=thought.confidence,
        )
