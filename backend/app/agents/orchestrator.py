"""Main workflow orchestrator for the PRD generation process."""

import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, List
from datetime import datetime, timedelta

from ..config import settings
from ..models import SessionPhase
from ..services.conversation_store import conversation_store
from ..utils.json_parser import extract_json_from_llm_response, validate_judge_response

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionContext:
    """Holds context for a session during processing."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at: datetime = datetime.utcnow()
        self.clarification_qa: List[Dict[str, str]] = []
        self.debate_messages: List[Dict[str, Any]] = []
        self.requirements: str = ""
        self.prd_content: str = ""
        self.judge_scores: Dict[str, Any] = {}

    def get_clarification_summary(self) -> str:
        """Get a summary of clarification Q&A."""
        if not self.clarification_qa:
            return "No clarification questions asked."

        summary = []
        for qa in self.clarification_qa:
            summary.append(f"Q: {qa['question']}")
            summary.append(f"A: {qa['answer']}")
            summary.append("")
        return "\n".join(summary)

    def get_debate_summary(self) -> str:
        """Get a summary of the debate."""
        if not self.debate_messages:
            return "No debate conducted."

        summary = []
        for msg in self.debate_messages:
            summary.append(f"[{msg['agent']}] ({msg['type']}): {msg['content'][:300]}...")
        return "\n\n".join(summary)


# Global session contexts
_session_contexts: Dict[str, SessionContext] = {}


def get_session_context(session_id: str) -> SessionContext:
    """Get or create session context."""
    if session_id not in _session_contexts:
        _session_contexts[session_id] = SessionContext(session_id)
    return _session_contexts[session_id]


def release_session_context(session_id: str) -> None:
    """Remove session context from memory when no longer needed."""
    _session_contexts.pop(session_id, None)


def cleanup_stale_contexts(timeout_minutes: int = 60) -> int:
    """Remove contexts older than timeout_minutes. Returns count removed."""
    cutoff = datetime.utcnow() - timedelta(minutes=timeout_minutes)
    stale = [sid for sid, ctx in _session_contexts.items() if ctx.created_at < cutoff]
    for sid in stale:
        del _session_contexts[sid]
    if stale:
        logger.info(f"Cleaned up {len(stale)} stale session context(s)")
    return len(stale)


async def run_clarification(session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Run the clarification phase, yielding events for SSE."""
    logger.info(f"[CLARIFY] Starting clarification for session {session_id}")

    session = conversation_store.get_session(session_id)
    if not session:
        yield {"type": "error", "data": {"error": "Session not found"}}
        return

    context = get_session_context(session_id)

    # Guard against infinite clarification loops
    if session.clarification_round >= settings.max_clarification_rounds:
        logger.info(f"[CLARIFY] Hit max rounds ({settings.max_clarification_rounds}), auto-completing")
        yield {"type": "complete", "data": {"message": "Maximum clarification rounds reached"}}
        return

    # Update phase
    session.phase = SessionPhase.CLARIFYING
    session.clarification_round += 1
    conversation_store.save_session(session)

    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from .definitions import CLARIFIER_AGENT

        logger.info(f"[CLARIFY] Creating fast model client for round {session.clarification_round}...")

        model_client = OpenAIChatCompletionClient(
            model=settings.model_name_fast,
            api_key=settings.openai_api_key,
        )

        # Build clarification prompt
        clarification_prompt = f"""PROJECT IDEA:
{session.idea}

PREVIOUS Q&A:
{context.get_clarification_summary()}

CURRENT ROUND: {session.clarification_round}

Generate 3-5 clarifying questions with multiple choice options.
Output ONLY valid JSON as specified in your instructions."""

        # Create clarifier agent
        clarifier = AssistantAgent(
            name="Clarifier",
            description=CLARIFIER_AGENT.description,
            system_message=CLARIFIER_AGENT.system_prompt,
            model_client=model_client,
        )

        team = RoundRobinGroupChat(
            participants=[clarifier],
            termination_condition=MaxMessageTermination(2),  # Task + Agent response
        )

        logger.info(f"[CLARIFY] Running clarifier agent...")
        result = await team.run(task=clarification_prompt)

        # Extract response content
        response_content = ""
        for msg in result.messages:
            if hasattr(msg, 'content') and msg.content and msg.source != "user":
                response_content = msg.content
                break

        logger.info(f"[CLARIFY] Raw response: {response_content[:500] if response_content else '(empty)'}...")

        # Parse JSON response
        fallback = {
            "questions": [],
            "is_complete": False
        }
        parsed_data, success, error = extract_json_from_llm_response(response_content, fallback)

        if not success:
            logger.warning(f"[CLARIFY] JSON parsing failed: {error}")

        # Check if clarification is complete
        if parsed_data.get("is_complete", False):
            logger.info(f"[CLARIFY] Clarification marked as complete by agent")
            conversation_store.append_clarification(
                session_id,
                f"## Round {session.clarification_round}\n\n_Clarification complete - sufficient information gathered._\n"
            )
            yield {"type": "complete", "data": {"message": "Clarification complete"}}
            return

        # Format questions for frontend
        questions = parsed_data.get("questions", [])
        if not questions:
            logger.warning(f"[CLARIFY] No questions generated, marking complete")
            yield {"type": "complete", "data": {"message": "Clarification complete"}}
            return

        formatted_questions = []
        for q in questions:
            formatted_q = {
                "question": q.get("question", ""),
                "context": q.get("context"),
                "options": q.get("options", []),
            }
            formatted_questions.append(formatted_q)

        logger.info(f"[CLARIFY] Generated {len(formatted_questions)} questions")

        # Save to transcript
        transcript_lines = [f"## Round {session.clarification_round}\n"]
        for i, q in enumerate(formatted_questions, 1):
            transcript_lines.append(f"**Q{i}:** {q['question']}")
            if q.get('context'):
                transcript_lines.append(f"_Context: {q['context']}_")
            for opt in q.get('options', []):
                transcript_lines.append(f"  - {opt.get('id', '?')}) {opt.get('text', '')}")
            transcript_lines.append("")
        conversation_store.append_clarification(session_id, "\n".join(transcript_lines))

        # Yield questions to frontend
        yield {
            "type": "questions",
            "data": {
                "questions": formatted_questions,
                "round_number": session.clarification_round,
            },
        }

    except Exception as e:
        logger.error(f"[CLARIFY] Error: {e}", exc_info=True)
        yield {"type": "error", "data": {"error": str(e)}}


async def process_answers(session_id: str, answers: List[Dict[str, Any]]) -> None:
    """Process user answers to clarifying questions."""
    session = conversation_store.get_session(session_id)
    if not session:
        raise ValueError("Session not found")

    context = get_session_context(session_id)

    transcript_lines = []
    for i, answer in enumerate(answers):
        # Extract the answer text - prefer custom_answer, then selected_option_text
        if answer.get("custom_answer"):
            answer_text = answer["custom_answer"]
        elif answer.get("selected_option_text"):
            answer_text = f"[{answer.get('selected_option', '?')}] {answer['selected_option_text']}"
        else:
            answer_text = answer.get("selected_option", "No answer")

        question_text = answer.get("question", f"Question {i + 1}")

        context.clarification_qa.append({
            "question": question_text,
            "answer": answer_text,
        })

        transcript_lines.append(f"**A{i+1}:** {answer_text}")

    conversation_store.append_clarification(
        session_id,
        "\n".join(transcript_lines) + "\n"
    )


def _get_agent_type(agent_name: str) -> str:
    """Convert agent name to agent type."""
    name_to_type = {
        "Architect": "architect",
        "DevOps": "devops",
        "Security": "security",
        "UX": "ux",
        "QA": "qa",
        "Product_Manager": "product_manager",
        "Data_Engineer": "data_engineer",
        "ML_Engineer": "ml_engineer",
        "Frontend_Dev": "frontend_dev",
        "Backend_Dev": "backend_dev",
        "Mobile_Dev": "mobile_dev",
        "Business_Analyst": "business_analyst",
        "Tech_Lead": "tech_lead",
        "Moderator": "moderator",
    }
    return name_to_type.get(agent_name, "moderator")


def _classify_message(content: str) -> str:
    """Classify message type based on content tags."""
    content_lower = content.lower()
    if "[proposal]" in content_lower:
        return "proposal"
    elif "[critique]" in content_lower:
        return "critique"
    elif "[agreement]" in content_lower:
        return "agreement"
    elif "[summary]" in content_lower:
        return "summary"
    return "proposal"


async def run_debate(session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Run the expert debate phase, yielding events for SSE in real-time."""
    logger.info(f"[DEBATE] Starting debate for session {session_id}")

    session = conversation_store.get_session(session_id)
    if not session or not session.config:
        yield {"type": "error", "data": {"error": "Session not configured"}}
        return

    context = get_session_context(session_id)

    # Get selected agents
    selected_agents = [a.value for a in session.config.selected_agents]
    num_rounds = session.config.debate_rounds

    logger.info(f"[DEBATE] Agents: {selected_agents}, Rounds: {num_rounds}")

    # Signal debate start
    yield {
        "type": "debate_start",
        "data": {
            "agents": selected_agents,
            "rounds": num_rounds,
        },
    }

    conversation_store.append_debate(
        session_id,
        f"# Expert Debate\n\nParticipants: {', '.join(selected_agents)}\nRounds: {num_rounds}\n"
    )

    # Build debate context
    debate_context = f"""PROJECT IDEA:
{session.idea}

CLARIFICATION SUMMARY:
{context.get_clarification_summary()}

You are participating in an expert debate to design the best solution for this project.
Each expert should contribute their unique perspective.
Build on each other's ideas and reach consensus on key decisions."""

    try:
        # Import here to avoid circular imports
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from .definitions import DEBATE_AGENTS, MODERATOR_AGENT

        logger.info(f"[DEBATE] Creating model clients (fast={settings.model_name_fast}, strong={settings.model_name})...")

        # Fast model for debate agents (bulk work)
        fast_client = OpenAIChatCompletionClient(
            model=settings.model_name_fast,
            api_key=settings.openai_api_key,
        )
        # Strong model for moderator (synthesis is high-leverage)
        strong_client = OpenAIChatCompletionClient(
            model=settings.model_name,
            api_key=settings.openai_api_key,
        )

        # Create agents with fast model
        agents = []
        for agent_id in selected_agents:
            if agent_id in DEBATE_AGENTS:
                defn = DEBATE_AGENTS[agent_id]
                agent = AssistantAgent(
                    name=defn.name.replace(" ", "_"),
                    description=defn.description,
                    system_message=defn.system_prompt,
                    model_client=fast_client,
                )
                agents.append(agent)
                logger.info(f"[DEBATE] Created agent: {defn.name} (fast)")

        # Add moderator with strong model
        mod_defn = MODERATOR_AGENT
        moderator = AssistantAgent(
            name=mod_defn.name,
            description=mod_defn.description,
            system_message=mod_defn.system_prompt,
            model_client=strong_client,
        )
        agents.append(moderator)
        logger.info(f"[DEBATE] Created moderator (strong)")

        # Run debate round by round
        for round_num in range(1, num_rounds + 1):
            logger.info(f"[DEBATE] === Starting Round {round_num}/{num_rounds} ===")

            yield {
                "type": "round_start",
                "data": {"round_number": round_num},
            }

            # Build round context
            round_context = f"""Round {round_num} of {num_rounds}.

{debate_context}

Previous discussion summary:
{context.get_debate_summary()[-2000:] if context.debate_messages else 'This is the first round.'}

Each expert should contribute one focused message. Tag your message with [PROPOSAL], [CRITIQUE], or [AGREEMENT].
The Moderator should provide a brief [SUMMARY] at the end."""

            # Use RoundRobinGroupChat for this round
            team = RoundRobinGroupChat(
                participants=agents,
                termination_condition=MaxMessageTermination(len(agents)),
            )

            logger.info(f"[DEBATE] Running round {round_num} with {len(agents)} agents...")

            try:
                result = await team.run(task=round_context)

                logger.info(f"[DEBATE] Round {round_num} complete, processing {len(result.messages)} messages")

                # Process and yield each message
                for msg in result.messages:
                    content = msg.content if hasattr(msg, 'content') else str(msg)
                    agent_name = msg.source if hasattr(msg, 'source') else "Unknown"

                    # Skip task messages
                    if agent_name == "user" or not content.strip():
                        continue

                    msg_type = _classify_message(content)

                    message_data = {
                        "agent": agent_name,
                        "content": content,
                        "round": round_num,
                        "type": msg_type,
                    }

                    context.debate_messages.append(message_data)

                    # Save to transcript
                    conversation_store.append_debate(
                        session_id,
                        f"### {agent_name} [{msg_type.upper()}] (Round {round_num})\n\n{content}\n"
                    )

                    logger.info(f"[DEBATE] {agent_name}: {content[:100]}...")

                    # Yield to SSE stream
                    yield {
                        "type": "message",
                        "data": {
                            "agent_name": agent_name,
                            "agent_type": _get_agent_type(agent_name),
                            "content": content,
                            "message_type": msg_type,
                            "round_number": round_num,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    }

            except Exception as round_error:
                logger.error(f"[DEBATE] Error in round {round_num}: {round_error}")
                yield {
                    "type": "error",
                    "data": {"error": f"Round {round_num} error: {str(round_error)}"},
                }
                continue

            # Update session
            session.debate_round = round_num
            conversation_store.save_session(session)

        logger.info(f"[DEBATE] All rounds complete, starting drafting phase...")

        # Run drafting phase
        session.phase = SessionPhase.DRAFTING
        conversation_store.save_session(session)

        yield {"type": "drafting_start", "data": {"message": "Synthesizing debate into PRD..."}}

        # Create PRD using a single agent
        prd_prompt = f"""Based on the following project idea and expert debate, create a comprehensive PRD.

PROJECT IDEA:
{session.idea}

EXPERT DEBATE SUMMARY:
{context.get_debate_summary()}

Create a PRD with these sections:
1. Executive Summary
2. Problem Statement
3. Solution Overview
4. Implementation Waves (Wave 0: Foundation, Wave 1: Core MVP, Wave 2: Enhanced, Wave 3: Polish)
5. Risk Assessment
6. Security Considerations
7. Testing Strategy
8. Open Questions
"""

        prd_agent = AssistantAgent(
            name="PRD_Writer",
            system_message="You are a technical writer who creates comprehensive PRDs. Write in clear markdown format.",
            model_client=strong_client,
        )

        prd_team = RoundRobinGroupChat(
            participants=[prd_agent],
            termination_condition=MaxMessageTermination(2),  # Task + Agent response
        )

        logger.info(f"[DEBATE] Generating PRD...")
        prd_result = await prd_team.run(task=prd_prompt)

        logger.debug(f"[DEBATE] PRD result has {len(prd_result.messages)} messages")
        for i, msg in enumerate(prd_result.messages):
            source = msg.source if hasattr(msg, 'source') else 'unknown'
            has_content = hasattr(msg, 'content') and msg.content
            logger.debug(f"[DEBATE] Message {i}: source={source}, has_content={has_content}")
            if hasattr(msg, 'content') and msg.content and msg.source != "user":
                context.prd_content = msg.content
                logger.info(f"[DEBATE] Extracted PRD content from {source} ({len(msg.content)} chars)")
                break

        # Validate PRD content was generated
        if not context.prd_content or not context.prd_content.strip():
            error_msg = "PRD generation failed: No content returned from drafting phase"
            logger.error(f"[DEBATE] {error_msg}")
            logger.debug(f"[DEBATE] prd_result.messages count: {len(prd_result.messages) if prd_result else 0}")
            yield {"type": "error", "data": {"error": error_msg, "phase": "drafting"}}
            return

        # Save the PRD
        conversation_store.save_prd(session_id, context.prd_content)
        logger.info(f"[DEBATE] PRD saved ({len(context.prd_content)} chars)")

        yield {"type": "complete", "data": {"message": "Debate and drafting complete"}}

    except Exception as e:
        logger.error(f"[DEBATE] Error: {e}", exc_info=True)
        yield {"type": "error", "data": {"error": str(e)}}


async def run_judicial_review(session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Run the judicial review phase, yielding events for SSE."""
    logger.info(f"[JUDGE] Starting judicial review for session {session_id}")

    session = conversation_store.get_session(session_id)
    if not session:
        yield {"type": "error", "data": {"error": "Session not found"}}
        return

    context = get_session_context(session_id)

    if not context.prd_content:
        prd_file = conversation_store.get_session_dir(session_id) / "PRD.md"
        if prd_file.exists():
            with open(prd_file, "r") as f:
                context.prd_content = f.read()
        else:
            yield {"type": "error", "data": {"error": "No PRD content available"}}
            return

    try:
        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.teams import RoundRobinGroupChat
        from autogen_agentchat.conditions import MaxMessageTermination
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from .definitions import JUDGE_AGENTS

        model_client = OpenAIChatCompletionClient(
            model=settings.model_name_fast,
            api_key=settings.openai_api_key,
        )

        conversation_store.append_review(session_id, "# Judicial Review\n")
        scores = {}

        for judge_type, judge_defn in JUDGE_AGENTS.items():
            logger.info(f"[JUDGE] Running {judge_type} judge...")

            yield {
                "type": "judge_start",
                "data": {"judge_type": judge_type},
            }

            judge_agent = AssistantAgent(
                name=judge_defn.name.replace(" ", "_"),
                system_message=judge_defn.system_prompt,
                model_client=model_client,
            )

            eval_prompt = f"""Evaluate the following PRD.

PROJECT IDEA:
{session.idea}

PRD CONTENT:
{context.prd_content[:8000]}

Provide your evaluation in JSON format as specified in your instructions."""

            team = RoundRobinGroupChat(
                participants=[judge_agent],
                termination_condition=MaxMessageTermination(2),  # Task + Judge response
            )

            result = await team.run(task=eval_prompt)

            evaluation = ""
            for msg in result.messages:
                if hasattr(msg, 'content') and msg.source != "user":
                    evaluation = msg.content
                    break

            logger.info(f"[JUDGE] {judge_type} raw response length: {len(evaluation)}")
            logger.info(f"[JUDGE] {judge_type} raw response preview: {evaluation[:300] if evaluation else '(empty)'}")

            # Parse JSON using robust parser
            fallback = {
                "scores": {},
                "reasoning": evaluation,
                "overall_score": 5.0,
                "recommendations": []
            }
            eval_data, success, error = extract_json_from_llm_response(evaluation, fallback)

            if not success:
                logger.warning(f"[JUDGE] {judge_type} JSON parsing failed: {error}")
                logger.debug(f"[JUDGE] Raw response preview: {evaluation[:500]}")

            # Validate and normalize the response structure
            eval_data, warnings = validate_judge_response(eval_data, judge_type)
            for w in warnings:
                logger.warning(f"[JUDGE] {w}")

            score_data = {
                "judge_name": judge_defn.name,
                "judge_type": judge_type,
                **eval_data,
            }
            scores[judge_type] = score_data
            context.judge_scores[judge_type] = score_data

            logger.info(f"[JUDGE] {judge_type} score: {eval_data.get('overall_score', 'N/A')}")

            conversation_store.append_review(
                session_id,
                f"## {judge_defn.name}\n\nOverall Score: {eval_data.get('overall_score', 'N/A')}\n\n{eval_data.get('reasoning', '')}\n"
            )

            yield {
                "type": "score",
                "data": score_data,
            }

        # Calculate verdict
        all_scores = [s.get("overall_score", 5.0) for s in scores.values()]
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 5.0

        if avg_score >= 8:
            verdict = "Excellent project plan. Ready for implementation with minor adjustments."
        elif avg_score >= 6:
            verdict = "Good project plan with some areas for improvement. Proceed with caution."
        elif avg_score >= 4:
            verdict = "Project plan needs significant revision before implementation."
        else:
            verdict = "Project plan requires major rework. Consider revisiting core assumptions."

        logger.info(f"[JUDGE] Average score: {avg_score:.1f}, Verdict: {verdict}")

        yield {
            "type": "verdict",
            "data": {
                "verdict": verdict,
                "average_score": avg_score,
            },
        }

        # Save scores
        result_data = {"scores": scores, "average_score": avg_score, "verdict": verdict}
        conversation_store.save_scores(session_id, result_data)

        # Update session
        session.phase = SessionPhase.COMPLETED
        conversation_store.save_session(session)

        # Generate README
        readme_content = _generate_readme(session, context, result_data)
        conversation_store.save_readme(session_id, readme_content)

        # Release session context from memory now that we're done
        release_session_context(session_id)

        yield {"type": "complete", "data": {"message": "Judicial review complete"}}

    except Exception as e:
        logger.error(f"[JUDGE] Error: {e}", exc_info=True)
        yield {"type": "error", "data": {"error": str(e)}}


def _generate_readme(session, context: SessionContext, judge_result: dict) -> str:
    """Generate the README.md file."""
    return f"""# PRD Package: {session.id}

Generated by PANEL — PRD from Agent Negotiation & Expert Logic

## Overview

This package contains a comprehensive Product Requirements Document (PRD) generated
through a multi-agent AI system involving:

1. **Clarification Phase**: AI-driven requirements elicitation
2. **Expert Debate**: Multiple specialized agents debating architecture, security, UX, etc.
3. **Judicial Review**: Three judges evaluating business viability, technical soundness, and feasibility

## Judge Scores

| Judge | Score |
|-------|-------|
| Business | {judge_result['scores'].get('business', {}).get('overall_score', 'N/A')}/10 |
| Technical | {judge_result['scores'].get('technical', {}).get('overall_score', 'N/A')}/10 |
| Feasibility | {judge_result['scores'].get('feasibility', {}).get('overall_score', 'N/A')}/10 |
| **Average** | **{judge_result['average_score']:.1f}/10** |

### Verdict

{judge_result['verdict']}

## Generated

- Session ID: {session.id}
- Generated: {datetime.utcnow().isoformat()}
- Model: {settings.model_name}

---

*Generated by PANEL — PRD from Agent Negotiation & Expert Logic*
"""
