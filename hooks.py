from __future__ import annotations
from pathlib import Path
from agents import AgentHooks, RunContextWrapper, TContext, Agent
import logging

logger = logging.getLogger(__name__)


class DefaultAgentHook(AgentHooks):
    def __init__(self, model: str, agent_name: str):
        self.turn = 0
        self.model = model
        self.name = agent_name

    async def on_llm_start(self, context, agent, system_prompt, input_items):
        self.turn += 1
        logger.info(f"\n[{self.name}] Turn {self.turn} model call started: {self.model}")

    async def on_llm_end(self, context, agent, response):
        usage = context.usage
        logger.info(f"[{self.name}] Turn {self.turn} model call completed")
        logger.info(
            f"           Usage: {usage.requests} requests, "
            f"{usage.input_tokens} input, "
            f"{usage.output_tokens} output, "
            f"{usage.total_tokens} total"
        )

    # todo - fix
    #async def on_handoff(self, context,from_agent: Agent[TContext],to_agent: Agent[TContext]) -> None:
    #    logger.info(f"[{self.name}] Turn {self.turn} handoff from {from_agent.name} to {to_agent.name}")

    async def on_tool_start(self, context, agent, tool):
        tool_name = getattr(tool, "name", type(tool).__name__)
        logger.info(f"Tool started: {tool_name}",)

        arguments = getattr(context, "tool_arguments", None)
        if arguments:
            text = str(arguments).replace("\n", " ")
            if len(text) > 500:
                text = text[:500] + "..."

            logger.info(f"Arguments: {text}")

    async def on_tool_end(self, context, agent, tool, result):
        tool_name = getattr(tool, "name", type(tool).__name__)
        logger.info(f"Tool completed: {tool_name}")

        if result is not None:
            text = str(result).replace("\n", " ")
            if len(text) > 300:
                text = text[:300] + "..."

            logger.info(f"Result: {text}")
