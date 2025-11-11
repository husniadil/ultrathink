import os
import uuid
from ..models.thought import Thought, ThoughtRequest, ThoughtResponse
from ..models.session import ThinkingSession, _parse_assumption_id


class UltraThinkService:
    """
    Service: Orchestrates the sequential thinking process
    Handles session lifecycle and coordinates between models and interface
    """

    def __init__(self) -> None:
        self._disable_logging = (
            os.environ.get("DISABLE_THOUGHT_LOGGING", "").lower() == "true"
        )
        self._sessions: dict[str, ThinkingSession] = {}

    def _resolve_cross_session_assumption(
        self, scoped_id: str, current_session_id: str
    ) -> tuple[str | None, bool]:
        """
        Resolve a cross-session assumption reference

        Args:
            scoped_id: Scoped assumption ID (e.g., "session-1:A1")
            current_session_id: Current session ID

        Returns:
            Tuple of (resolved_local_id, was_resolved)
            - If resolved: ("A1", True) - assumption exists in target session
            - If unresolved: (None, False) - session or assumption not found

        Examples:
            "session-1:A1" where session-1 has A1 -> ("A1", True)
            "nonexistent:A1" -> (None, False)
            "session-1:A99" where A99 doesn't exist -> (None, False)
        """
        target_session_id, local_id = _parse_assumption_id(scoped_id)

        if target_session_id is None:
            # Not a cross-session reference
            return scoped_id, True

        # Check if target session exists
        if target_session_id not in self._sessions:
            return None, False

        # Check if assumption exists in target session
        target_session = self._sessions[target_session_id]
        if local_id not in target_session.all_assumptions:
            return None, False

        return local_id, True

    def process_thought(self, request: ThoughtRequest) -> ThoughtResponse:
        """
        Process a thought request

        Args:
            request: ThoughtRequest from interface layer

        Returns:
            ThoughtResponse for interface layer

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

        # Auto-assign next_thought_needed if not provided
        if request.next_thought_needed is None:
            next_thought_needed = thought_number < request.total_thoughts
        else:
            next_thought_needed = request.next_thought_needed

        # Validate cross-session assumption references
        validated_cross_session_refs: list[str] = []
        if request.depends_on_assumptions:
            for assumption_id in request.depends_on_assumptions:
                if ":" in assumption_id:  # Cross-session reference
                    _, was_resolved = self._resolve_cross_session_assumption(
                        assumption_id, session_id
                    )
                    if was_resolved:
                        validated_cross_session_refs.append(assumption_id)

        # Translate request to thought model (exclude session_id, override auto-assigned fields)
        thought_data = request.model_dump(exclude={"session_id"})
        thought_data["thought_number"] = thought_number
        thought_data["next_thought_needed"] = next_thought_needed
        thought = Thought(**thought_data)

        # Execute business logic
        session.add_thought(thought, validated_cross_session_refs)

        # Collect unresolved references and warnings from session
        unresolved = session.unresolved_references
        warnings = session.cross_session_warnings

        # Return response
        return ThoughtResponse(
            session_id=session_id,
            thought_number=thought.thought_number,
            total_thoughts=thought.total_thoughts,
            next_thought_needed=thought.next_thought_needed,
            branches=session.branch_ids,
            thought_history_length=session.thought_count,
            confidence=thought.confidence,
            uncertainty_notes=thought.uncertainty_notes,
            outcome=thought.outcome,
            all_assumptions=session.all_assumptions,
            risky_assumptions=session.risky_assumptions,
            falsified_assumptions=session.falsified_assumptions,
            unresolved_references=unresolved,
            cross_session_warnings=warnings,
        )
