from agents import Agent, handoff, RunContextWrapper, AgentHooks, TContext, Tool
import yaml
import logging
from typing import Any
import tool_registry
from hooks import DefaultAgentHook



def build_agents(config: dict):
    """ Function to load the config file and build the agents. Uses registries to connect tools.
     """
    tool_registry.build_registries()

    agent_registry = {}

    try:
        for name, cfg in config.items():
            model = cfg.get("model", "gpt-4o-mini")
            hooks = DefaultAgentHook(model, name)
            agent = Agent(
                name=name,
                handoff_description=cfg["handoff_description"],
                instructions=cfg["instructions"],
                model=cfg.get("model", "gpt-4o-mini"),
                hooks=hooks,
                tools=[]
            )
            agent_registry[name] = agent

            tools = []
            if "tools" in cfg:
                for tool_id in cfg["tools"]:
                    if tool_id in tool_registry.TOOL_REGISTRY:
                        tools.append(tool_registry.TOOL_REGISTRY[tool_id])
                    else:
                        raise ValueError(f"Tool not found: {tool_id}")
            #agent.tools = tools
            agent_registry[name].tools = tools

    except Exception as e:
        logging.error(f"Error occurred during agent configuration:\n{e}")

    # Second pass to configure hand-offs (requires agents to exist first)
    try:
        for name, cfg in config.items():
            handoff_defs = cfg.get("handoffs", [])
            handoffs = []
            for h in handoff_defs:
                if isinstance(h, dict):
                    target_agent = agent_registry[h["agent"]]
                    handoffs.append(handoff(target_agent))
                else:
                    raise ValueError(f"Invalid handoff for agent '{name}': {h}")

            agent_registry[name].handoffs = handoffs

    except Exception as e:
        logging.error(f"Error occurred during agent handoff configuration:\n{e}")

    return agent_registry
