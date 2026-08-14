"""
test_handoff.py - Unit tests for Specialist Agent Handoff (Day 9 Task).
"""

from unittest.mock import AsyncMock, MagicMock
import pytest

from agent import Assistant
from scheme_specialist import SchemeSpecialist, SCHEME_SPECIALIST_PROMPT


def test_scheme_specialist_initialization():
    specialist = SchemeSpecialist()
    assert specialist.instructions == SCHEME_SPECIALIST_PROMPT
    assert specialist.caller_name == "Citizen"
    assert specialist.language == "Hindi"
    assert hasattr(specialist, "check_scheme_eligibility")
    assert hasattr(specialist, "lookup_caller")
    assert hasattr(specialist, "save_caller_info")
    assert hasattr(specialist, "create_escalation")


def test_assistant_has_transfer_tool():
    assistant = Assistant()
    assert hasattr(assistant, "transfer_to_scheme_specialist")


@pytest.mark.asyncio
async def test_transfer_to_scheme_specialist_execution():
    assistant = Assistant()
    assistant.caller_name = "Rajesh"
    assistant.language = "Hindi"
    assistant._current_call_id = "test-call-123"

    mock_session = MagicMock()
    mock_session.say = AsyncMock()
    mock_session.update_agent = MagicMock()

    mock_context = MagicMock()
    mock_context.session = mock_session

    result = await assistant.transfer_to_scheme_specialist(
        context=mock_context,
        reason_or_query="Detailed inquiry about PM Kisan and PMAY eligibility rules",
    )

    assert "Successfully transferred caller" in result
    mock_session.say.assert_called_once_with(
        "I am connecting you to our Government Schemes Specialist. Please hold on a moment."
    )
    mock_session.update_agent.assert_called_once()

    # Check that update_agent was called with a SchemeSpecialist instance that inherited state
    call_arg = mock_session.update_agent.call_args[0][0]
    assert isinstance(call_arg, SchemeSpecialist)
    assert call_arg.caller_name == "Rajesh"
    assert call_arg.language == "Hindi"
    assert call_arg._current_call_id == "test-call-123"


@pytest.mark.asyncio
async def test_specialist_on_enter_introduces_itself():
    specialist = SchemeSpecialist()
    mock_session = MagicMock()
    mock_session.say = AsyncMock()
    specialist._activity = MagicMock(session=mock_session)

    await specialist.on_enter()

    mock_session.say.assert_called_once()
    spoken_text = mock_session.say.call_args[0][0]
    assert "Government Schemes Specialist" in spoken_text
    assert "PM Kisan" in spoken_text
    assert "PM Awas Yojana" in spoken_text
