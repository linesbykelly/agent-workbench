# Agents Workbench

A lightweight web app for building, configuring, and testing agent workflows with the OpenAI Agents SDK.

---

## 🚀 Features

- **Agent Configuration**
  - Create and edit agents through a simple web UI.
  - Configure models, instructions, tools, entry-point behavior, and agent handoffs.
  - Update existing agents without recreating them.
  - Save your agent configuration as a `.json` file.
  - Load previously saved configurations.

- **Interactive Chat**
  - Test your configured agents directly from the web interface.
  - Configure an entry-point agent to determine which agent starts a conversation.
  - Use agent handoffs to build multi-agent workflows.

- **Custom Function Tools**
  - Add new tools by creating functions in the `tools/` directory.
  - Tools are automatically discovered and registered.
  - Functions must be decorated with `@function_tool`.

- **Shared File Storage**
  - Tools can create and read files from the shared `files/` directory.
  - This allows agents to work with files they create as well as files provided by the user.
  - Supported tools can create CSV files, text files, PowerPoint presentations, plots, and other file types.

> 💡 **Tip:** You can monitor agent traces, token usage, and tool calls through the [OpenAI dashboard](https://platform.openai.com/usage).

---

## 🛠️ How It Works

1. Start the application and open the Agent Workbench in your browser.
2. Create an agent using the configuration form.
3. Select a model and provide instructions for the agent.
4. Add any tools the agent should be able to use.
5. Configure handoffs if the agent should be able to delegate work to another agent.
6. Mark an agent as the **Entry point agent** if it should start conversations.
7. Use the chat interface to test your agents.
8. Save your configuration when you're finished.
9. Load a previously saved `.json` configuration to continue working on it later.
---

## 🧩 Example of saved `agents_config.json` output

```json
{
  "agents": {
    "product_helper": {
      "name": "Product Helper",
      "handoff_description": "Helps refine product specifications",
      "model": "gpt-4.1-mini",
      "tools": [
        "read_csv",
        "write_csv"
      ],
      "handoffs": [],
      "instructions": "You're a helpful product assistant...",
      "start_conversation": true
    }
  }
}

```
---

## 🧪 Try It Out
```bash
git clone https://github.com/linesbykelly/agent-workbench.git
cd agent-workbench
pip install -r requirements.txt
python app.py --openai_api-key your-api-key-here
```
Then open http://localhost:7860 in your browser.

---
## 📂 Folder Structure
```yml
agents-poc-tool/
├── app.py                  # Main Gradio application
├── hooks.py                # Agent hooks
├── tool_registry.py        # Discovers and registers tools
├── load_agents.py          # Builds agents from configuration
├── tools/                  # Custom agent tools
│   ├── files.py
│   ├── csv_tools.py
│   ├── pptx_tools.py
│   └── ...
├── files/                  # Shared input/output files
├── logs/                   # Application logs
├── utils.py                # Shared utility functions
├── requirements.txt
└── README.md
```
