from agents import Runner
import time
import gradio as gr
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import json
import tempfile
from pathlib import Path
# Internal
from tool_registry import TOOL_REGISTRY, build_registries
import load_agents
from utils import get_text_gen_models


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        TimedRotatingFileHandler(
            "./logs/AppLogs.log",
            when="midnight",
            interval=1,
            backupCount=7
        )
    ],
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)

build_registries()

AGENT_REGISTRY = {}
agents_config = {}

model_options = get_text_gen_models()


def get_starter_agent():
    if not AGENT_REGISTRY:
        logger.warning("No agents are configured.")
        return None

    starter_key = next(
        (
            key
            for key, config in agents_config.items()
            if config.get("start_conversation") is True
        ),
        None
    )

    if starter_key is not None:
        return AGENT_REGISTRY[starter_key]

    starter_key = next(iter(AGENT_REGISTRY))

    logger.warning(
        "No agent is configured as the conversation starter. "
        "Using first agent: %s",
        starter_key
    )

    return AGENT_REGISTRY[starter_key]


async def run_agents(user_msg, history):
    try:
        starter_agent = get_starter_agent()
        if starter_agent is None:
            return "No agents have been configured yet."

        logger.info(
            "Starting conversation with agent: %s",
            starter_agent.name
        )

        input = history + [
            {
                "role": "user",
                "content": user_msg
            }
        ]

        result = await Runner.run(
            starter_agent,
            input
        )

        logger.info(
            "Agent final output: %s",
            result.final_output
        )

        return result.final_output, True

    except Exception as e:
        logger.exception("Agent run failed")
        gr.Warning(f"Message was not sent: {e}")

        return f"*Message not sent: {user_msg}*", False


def get_agent_names():
    return [
        config["name"]
        for config in agents_config.values()
    ]


def handle_submit(
    agent_name,
    description,
    model,
    start_conversation,
    tools,
    handoffs,
    instructions
):
    global AGENT_REGISTRY

    agent_name = agent_name.strip()
    if not agent_name:
        gr.Warning("Agent name is required.")

        return (
            agents_config,
            gr.skip(),
            gr.update(value=agent_name),
            gr.update(value=description),
            gr.update(value=model),
            gr.update(value=start_conversation),
            gr.update(value=tools),
            gr.update(value=instructions),
            gr.skip()
        )

    if not model:
        gr.Warning("Model is required.")
        return (
            agents_config,
            gr.skip(),
            gr.update(value=agent_name),
            gr.update(value=description),
            gr.update(value=model),
            gr.update(value=start_conversation),
            gr.update(value=tools),
            gr.update(value=instructions),
            gr.skip()
        )

    # Create internal agent key
    agent_key = agent_name.replace(" ", "_").lower()

    action = (
        "updated"
        if agent_key in agents_config
        else "added"
    )

    # Only one starter agent
    if start_conversation:
        for key in agents_config:
            agents_config[key]["start_conversation"] = False

    # Convert handoff names -> keys
    name_to_key = {
        config["name"]: key
        for key, config in agents_config.items()
    }

    handoff_keys = [
        {"agent": name_to_key[name]}
        for name in handoffs
        if name in name_to_key
    ]

    # Save agent
    agents_config[agent_key] = {
        "name": agent_name,
        "handoff_description": description,
        "model": model,
        "start_conversation": start_conversation,
        "tools": tools,
        "handoffs": handoff_keys,
        "instructions": instructions
    }

    # Rebuild agent registry
    AGENT_REGISTRY = load_agents.build_agents(
        agents_config
    )

    # Update agent selector
    agent_keys = list(agents_config.keys())

    agents_update = gr.update(
        choices=agent_keys,
        value=None
    )

    gr.Info(f"Agent '{agent_key}' {action}.")

    return (
        agents_config,
        agents_update,
        gr.update(value=""),      # agent_name
        gr.update(value=""),      # description
        gr.update(value=None),    # model
        gr.update(value=False),   # start_conversation
        gr.update(value=[]),      # tools
        gr.update(value=""),      # instructions
        gr.update(value="➕ Add Agent")
    )


def update_handoff_dropdown():
    """
    Update the handoff dropdown after an agent has
    been added or loaded.
    """
    return gr.Dropdown(
        choices=get_agent_names(),
        value=[],
        multiselect=True,
        interactive=True,
        label="Handoff Agents"
    )


def handle_clear():
    global AGENT_REGISTRY

    agents_config.clear()
    AGENT_REGISTRY = {}

    return (
        {},
        gr.update(
            choices=[""],
            value=""
        ),
        gr.Dropdown(
            choices=[],
            value=[],
            multiselect=True,
            interactive=False,
            label="Handoff Agents"
        )
    )


def handle_save():
    if not agents_config:
        gr.Error("No agents to save.")

        return gr.update(
            visible=False
        )

    full_config = {
        "agents": agents_config
    }

    tmpdir = tempfile.mkdtemp()

    save_path = os.path.join(
        tmpdir,
        "agents_config.json"
    )

    with open(save_path, "w") as f:
        json.dump(
            full_config,
            f,
            indent=2
        )

    gr.Info("Config saved. Click to download.")

    return gr.update(
        value=save_path,
        visible=True
    )


def handle_load(file_obj):
    global agents_config, AGENT_REGISTRY

    try:
        with open(file_obj.name, "r") as f:
            loaded_data = json.load(f)

        # Validate top-level structure
        if (
            not isinstance(loaded_data, dict)
            or "agents" not in loaded_data
        ):
            gr.Error("Invalid file: top-level 'agents' key missing.")

            return (
                agents_config,
                gr.skip(),
                gr.skip()
            )

        agents = loaded_data["agents"]

        if not isinstance(agents, dict):
            gr.Error("Invalid file: 'agents' must be a dictionary.")

            return (
                agents_config,
                gr.skip(),
                gr.skip()
            )

        # Validate agents
        for key, config in agents.items():

            if not isinstance(config, dict):
                gr.Error(f"Agent '{key}' config must be a dictionary.")

                return (
                    agents_config,
                    gr.skip(),
                    gr.skip()
                )

            required_keys = [
                "name",
                "handoff_description",
                "model",
                "instructions"
            ]

            for required_key in required_keys:

                if required_key not in config:
                    gr.Error(
                        f"Agent '{key}' missing required field "
                        f"'{required_key}'."
                    )

                    return (
                        agents_config,
                        gr.skip(),
                        gr.skip()
                    )

            config.setdefault(
                "start_conversation",
                False
            )

            config.setdefault(
                "tools",
                []
            )

            config.setdefault(
                "handoffs",
                []
            )

        # Replace current configuration
        agents_config = agents

        # Rebuild registry
        AGENT_REGISTRY = load_agents.build_agents(
            agents_config
        )

        # Update agent selector
        agents_update = gr.update(
            choices=[""] + list(agents_config.keys()),
            value=""
        )

        gr.Info("Agents loaded.")

        return (
            agents_config,
            agents_update,
            gr.Dropdown(
                choices=get_agent_names(),
                value=[],
                multiselect=True,
                interactive=True,
                label="Handoff Agents"
            )
        )

    except Exception as e:

        logger.exception(
            "Error loading agent configuration."
        )

        gr.Error(f"Error loading file: {str(e)}")

        return (
            agents_config,
            gr.skip(),
            gr.skip()
        )


def load_agent(agent_key):

    if agent_key not in agents_config:
        return (
            "",
            "",
            None,
            False,
            [],
            gr.Dropdown(
                choices=get_agent_names(),
                value=[],
                multiselect=True,
                interactive=True,
                label="Handoff Agents"
            ),
            "",
            gr.update(value="➕ Add Agent")
        )

    agent = agents_config[agent_key]

    # Handoff choices
    handoff_choices = [
        config["name"]
        for key, config in agents_config.items()
        if key != agent_key
    ]

    # Existing handoffs
    selected_handoff_names = []

    for handoff in agent.get("handoffs", []):

        handoff_key = handoff["agent"]

        if handoff_key in agents_config:
            selected_handoff_names.append(
                agents_config[handoff_key]["name"]
            )

    # Return agent information
    return (
        agent["name"],
        agent["handoff_description"],
        agent["model"],
        agent.get("start_conversation", False),
        agent.get("tools", []),
        gr.Dropdown(
            choices=handoff_choices,
            value=selected_handoff_names,
            multiselect=True,
            interactive=True,
            label="Handoff Agents"
        ),
        agent["instructions"],
        gr.update(value="✏️ Update Agent")
    )


with gr.Blocks() as demo:

    gr.Markdown(
        "# 🤖 Agent Workbench\n"
        "Use the form to build your agents and test them in the chat below."
    )

    with gr.Row():

        with gr.Column(scale=2):

            gr.Markdown("### Agent Configuration")

            agent_selector = gr.Dropdown(
                label="Create a new agent or edit an existing one below",
                choices=[""],
                interactive=True
            )

            agent_name = gr.Textbox(
                label="Agent Name",
                placeholder="e.g. Orchestration Agent"
            )

            description = gr.Textbox(
                label="Description",
                placeholder="What does this agent do?"
            )

            model = gr.Dropdown(
                choices=model_options,
                label="Model"
            )

            start_conversation = gr.Checkbox(
                label="Entry point agent",
                value=False
            )

            handoffs = gr.Dropdown(
                choices=[],
                label="Handoff Agents",
                multiselect=True,
                interactive=False
            )

            tools = gr.Dropdown(
                choices=TOOL_REGISTRY.keys(),
                label="Tools",
                multiselect=True
            )

            instructions = gr.Textbox(
                label="Agent Instructions",
                lines=10,
                placeholder="Write agent instructions here..."
            )

            submit_btn = gr.Button(
                "➕ Add Agent"
            )

        with gr.Column(scale=1):

            gr.Markdown("### 📄 Current Config")

            output_json = gr.JSON(
                label="Agents Config Output",
                height=600
            )

            save_btn = gr.Button(
                "💾 Save Config"
            )

            file_output = gr.File(
                label="Config File Ready for Download",
                interactive=False,
                visible=False
            )

            clear_btn = gr.Button(
                "🗑️ Clear All Agents"
            )

            load_btn = gr.UploadButton(
                "📁 Load Existing Config",
                file_types=[".json"]
            )

        # ADD / UPDATE AGENT
        submit_event = submit_btn.click(
            handle_submit,
            inputs=[
                agent_name,
                description,
                model,
                start_conversation,
                tools,
                handoffs,
                instructions
            ],
            outputs=[
                output_json,
                agent_selector,
                agent_name,
                description,
                model,
                start_conversation,
                tools,
                instructions,
                submit_btn
            ]
        )

        # Update handoffs AFTER handle_submit finishes.
        # The first event modifies agents_config.
        # The second event then reads the updated agents_config.
        submit_event.then(
            update_handoff_dropdown,
            inputs=[],
            outputs=handoffs
        )

        # SELECT EXISTING AGENT
        agent_selector.change(
            load_agent,
            inputs=[agent_selector],
            outputs=[
                agent_name,
                description,
                model,
                start_conversation,
                tools,
                handoffs,
                instructions,
                submit_btn
            ]
        )

        # CLEAR ALL
        clear_btn.click(
            handle_clear,
            outputs=[
                output_json,
                agent_selector,
                handoffs
            ]
        )

        # SAVE
        save_btn.click(
            handle_save,
            outputs=[
                file_output
            ]
        )

        # LOAD
        load_btn.upload(
            handle_load,
            inputs=[load_btn],
            outputs=[
                output_json,
                agent_selector,
                handoffs
            ]
        )

    gr.Markdown("# 💬 Chat with your Agents")

    chatbot = gr.Chatbot(
        type="messages",
        label="Agent Chat"
    )

    msg = gr.Textbox(
        placeholder="Type a message and hit Enter..."
    )

    clear = gr.ClearButton(
        [msg, chatbot]
    )

    async def respond(message, chat_history):

        chat_history.append({
            "role": "user",
            "content": message
        })

        assistant_resp, success = await run_agents(
            message,
            chat_history[:-1]
        )

        if success:
            chat_history.append({
                "role": "assistant",
                "content": assistant_resp
            })
        else:
            chat_history[-1]["content"] = f"*Message not sent: {message}*"

        #time.sleep(1)

        return "", chat_history

    msg.submit(
        respond,
        [msg, chatbot],
        [msg, chatbot]
    )


demo.launch()