"""GroupChat configurations for different phases."""

from typing import List, Optional, Callable, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

from ..config import settings
from .definitions import (
    CLARIFIER_AGENT,
    MODERATOR_AGENT,
    SYNTHESIZER_AGENT,
    PRD_WRITER_AGENT,
    DEBATE_AGENTS,
    JUDGE_AGENTS,
    AgentDefinition,
)


def get_model_client() -> OpenAIChatCompletionClient:
    """Get the OpenAI model client."""
    return OpenAIChatCompletionClient(
        model=settings.model_name,
        api_key=settings.openai_api_key,
    )


def create_agent(definition: AgentDefinition, model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """Create an AutoGen agent from a definition."""
    return AssistantAgent(
        name=definition.name.replace(" ", "_"),
        description=definition.description,
        system_message=definition.system_prompt,
        model_client=model_client,
    )


class ClarificationTeam:
    """Team for the clarification phase using RoundRobinGroupChat."""

    def __init__(self):
        self.model_client = get_model_client()
        self.clarifier = create_agent(CLARIFIER_AGENT, self.model_client)

        # Termination condition: look for CLARIFICATION_COMPLETE
        self.termination = TextMentionTermination("CLARIFICATION_COMPLETE")

    async def run_round(self, context: str, max_messages: int = 2):
        """Run a single clarification round."""
        team = RoundRobinGroupChat(
            participants=[self.clarifier],
            termination_condition=self.termination | MaxMessageTermination(max_messages),
        )

        result = await team.run(task=context)
        return result


class DebateTeam:
    """Team for the expert debate phase using SelectorGroupChat."""

    def __init__(self, selected_agent_ids: List[str]):
        self.model_client = get_model_client()
        self.agents = []

        # Create selected expert agents
        for agent_id in selected_agent_ids:
            if agent_id in DEBATE_AGENTS:
                agent = create_agent(DEBATE_AGENTS[agent_id], self.model_client)
                self.agents.append(agent)

        # Always add moderator
        self.moderator = create_agent(MODERATOR_AGENT, self.model_client)
        self.agents.append(self.moderator)

    def _create_selector_prompt(self) -> str:
        """Create the selector prompt for choosing next speaker."""
        agent_names = [a.name for a in self.agents]
        return f"""You are the speaker selector for a technical debate.
Available speakers: {', '.join(agent_names)}

Select the next speaker based on:
1. Who hasn't spoken recently
2. Who has relevant expertise for the current topic
3. The Moderator should speak after every 3-4 other speakers to summarize

Respond with just the speaker name, nothing else."""

    async def run_round(self, context: str, round_number: int, messages_per_round: int = 6):
        """Run a single debate round."""
        task = f"""Round {round_number} of the expert debate.

Context and requirements:
{context}

Each expert should contribute their perspective. The moderator should summarize at the end.
Focus on reaching consensus on key decisions."""

        team = SelectorGroupChat(
            participants=self.agents,
            model_client=self.model_client,
            termination_condition=MaxMessageTermination(messages_per_round),
            selector_prompt=self._create_selector_prompt(),
        )

        result = await team.run(task=task)
        return result

    async def run_full_debate(
        self,
        context: str,
        num_rounds: int,
        on_message: Optional[Callable[[dict], Any]] = None
    ):
        """Run the full debate with multiple rounds."""
        all_messages = []

        for round_num in range(1, num_rounds + 1):
            # Build context including previous rounds
            round_context = context
            if all_messages:
                round_context += "\n\nPrevious discussion:\n"
                for msg in all_messages[-10:]:  # Last 10 messages for context
                    round_context += f"{msg['agent']}: {msg['content'][:200]}...\n"

            result = await self.run_round(round_context, round_num)

            # Process messages from this round
            for msg in result.messages:
                message_data = {
                    "agent": msg.source,
                    "content": msg.content if hasattr(msg, 'content') else str(msg),
                    "round": round_num,
                    "type": self._classify_message(msg.content if hasattr(msg, 'content') else ""),
                }
                all_messages.append(message_data)

                if on_message:
                    await on_message(message_data)

        return all_messages

    def _classify_message(self, content: str) -> str:
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
        return "proposal"  # Default


class DraftingTeam:
    """Team for synthesizing debate into PRD."""

    def __init__(self):
        self.model_client = get_model_client()
        self.synthesizer = create_agent(SYNTHESIZER_AGENT, self.model_client)
        self.prd_writer = create_agent(PRD_WRITER_AGENT, self.model_client)

    async def run(self, project_idea: str, clarification_summary: str, debate_summary: str) -> dict:
        """Run the drafting phase to produce requirements and PRD."""
        # First, synthesize the debate into requirements
        synthesis_task = f"""Based on the following project idea and expert debate, extract structured requirements.

PROJECT IDEA:
{project_idea}

CLARIFICATION SUMMARY:
{clarification_summary}

DEBATE SUMMARY:
{debate_summary}

Synthesize these into a structured requirements document."""

        synthesis_team = RoundRobinGroupChat(
            participants=[self.synthesizer],
            termination_condition=MaxMessageTermination(1),
        )
        synthesis_result = await synthesis_team.run(task=synthesis_task)

        requirements = ""
        for msg in synthesis_result.messages:
            if hasattr(msg, 'content'):
                requirements = msg.content
                break

        # Then, write the PRD
        prd_task = f"""Write a comprehensive PRD based on these requirements.

PROJECT IDEA:
{project_idea}

REQUIREMENTS:
{requirements}

Create a PRD following the standard structure with implementation waves."""

        prd_team = RoundRobinGroupChat(
            participants=[self.prd_writer],
            termination_condition=MaxMessageTermination(1),
        )
        prd_result = await prd_team.run(task=prd_task)

        prd_content = ""
        for msg in prd_result.messages:
            if hasattr(msg, 'content'):
                prd_content = msg.content
                break

        return {
            "requirements": requirements,
            "prd": prd_content,
        }


class JudgingTeam:
    """Team for the judicial review phase."""

    def __init__(self):
        self.model_client = get_model_client()
        self.judges = {
            judge_type: create_agent(definition, self.model_client)
            for judge_type, definition in JUDGE_AGENTS.items()
        }

    async def run(
        self,
        project_idea: str,
        prd_content: str,
        on_score: Optional[Callable[[dict], Any]] = None
    ) -> dict:
        """Run the judicial review."""
        scores = {}

        for judge_type, judge in self.judges.items():
            task = f"""Evaluate the following PRD for a project.

PROJECT IDEA:
{project_idea}

PRD CONTENT:
{prd_content}

Provide your evaluation in the specified JSON format."""

            team = RoundRobinGroupChat(
                participants=[judge],
                termination_condition=MaxMessageTermination(1),
            )
            result = await team.run(task=task)

            # Extract the evaluation
            evaluation = None
            for msg in result.messages:
                if hasattr(msg, 'content'):
                    evaluation = msg.content
                    break

            # Parse the JSON evaluation
            import json
            try:
                # Try to extract JSON from the response
                json_start = evaluation.find('{')
                json_end = evaluation.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    eval_data = json.loads(evaluation[json_start:json_end])
                else:
                    eval_data = {
                        "scores": {},
                        "reasoning": evaluation,
                        "overall_score": 5.0,
                        "recommendations": [],
                    }
            except json.JSONDecodeError:
                eval_data = {
                    "scores": {},
                    "reasoning": evaluation,
                    "overall_score": 5.0,
                    "recommendations": [],
                }

            scores[judge_type] = {
                "judge_name": judge.name,
                "judge_type": judge_type,
                **eval_data,
            }

            if on_score:
                await on_score(scores[judge_type])

        # Calculate overall verdict
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

        return {
            "scores": scores,
            "average_score": avg_score,
            "verdict": verdict,
        }
