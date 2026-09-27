
import pytest
from unittest.mock import AsyncMock

from app.agent.workflow import healthcare_graph


def make_state(question):
    return {
        "messages": [
            {"role": "user", "content": question}
        ],
        "user_id": 2,
        "intent": None,
        "response": None,
        "pending_booking": None,
        "thread_id": None,
        "requires_confirmation": False,
    }


@pytest.mark.asyncio
async def test_healthcare_workflow(monkeypatch):
    question = "What are diabetes symptoms?"

    mock_agent = AsyncMock(
        return_value="Diabetes can cause increased thirst."
    )

    monkeypatch.setattr(
        "app.agent.workflow.run_agent",
        mock_agent
    )

    result = await healthcare_graph.ainvoke(
        make_state(question)
    )

    assert result["intent"] == "healthcare"
    assert result["response"] == (
        "Diabetes can cause increased thirst."
    )

    mock_agent.assert_awaited_once_with(question, 2)


@pytest.mark.asyncio
async def test_doctor_workflow(monkeypatch):
    question = "Find a cardiologist"

    mock_agent = AsyncMock(
        return_value="Dr. Sharma is a cardiologist."
    )

    monkeypatch.setattr(
        "app.agent.workflow.run_agent",
        mock_agent
    )

    result = await healthcare_graph.ainvoke(
        make_state(question)
    )

    assert result["intent"] == "doctor"
    assert result["response"] == (
        "Dr. Sharma is a cardiologist."
    )

    mock_agent.assert_awaited_once_with(question, 2)


@pytest.mark.asyncio
async def test_appointment_availability_workflow(monkeypatch):
    question = (
        "Find available slots for Dr. Sharma "
        "on 2026-09-30."
    )

    mock_agent = AsyncMock(
        return_value="11:30 AM and 12:00 PM are available."
    )

    monkeypatch.setattr(
        "app.agent.workflow.run_agent",
        mock_agent
    )

    result = await healthcare_graph.ainvoke(
        make_state(question)
    )

    assert result["intent"] == "appointment"
    assert result["response"] == (
        "11:30 AM and 12:00 PM are available."
    )
    assert result["requires_confirmation"] is False

    mock_agent.assert_awaited_once_with(question, 2)
    