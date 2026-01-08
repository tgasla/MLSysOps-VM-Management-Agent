[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18177473.svg)](https://doi.org/10.5281/zenodo.18177473)

# DRL VM Management Agent (ONNX)

This repository contains a Deep Reinforcement Learning agent (trained using Maskable PPO) for optimizing Virtual Machine placement and lifecycle management. The model is exported as a platform-independent **ONNX** file for easy deployment.

It includes a complete inference pipeline that handles raw JSON infrastructure states, serializes them for the neural network, and translates the output into human-readable actions.

## 📂 Project Structure

```text
.
├── model/
│   ├── vm_management_agent.onnx   # The trained Neural Network
│   └── model_config.json          # Model Card & Configuration
├── src/
│   ├── inference_engine.py        # Wraps ONNX runtime for predictions
│   ├── infra_state_serializer.py  # Converts JSON tree -> 801-dim Float Vector
│   └── action_interpreter.py      # Converts Model Output -> Human-readable Strings
├── demo.py                        # Main entry point to run all test scenarios
├── generate_scenarios.py          # Script to generate test JSON files
├── requirements.txt               # Python dependencies
└── README.md
```

## ⚠️ Limitations & Model Constraints
This agent is specialized for a specific environment configuration. The model weights are tied to these boundary conditions:

- **Maximum Scale:** The agent supports up to 32 Hosts within a single Datacenter.

- **Resource Metric:** Optimization is based solely on CPU Cores. Other resources (RAM, Disk, Network) are not considered in this version.

- **Job Constraints:** The maximum size for a single incoming job is 8 Cores.

The `total_job_cores_waiting` passed to the model is clamped to never exceed the largest VM size (8 cores).

**Input Structure:** The model expects strictly two inputs:

**Infrastructure State:** A flattened vector of fixed length (801 floats) representing the recursive tree of the Datacenter.

**Job Demand:** A single scalar value representing the total waiting job cores.

## 🛠️ Installation

It is recommended to use a virtual environment to keep dependencies isolated.

### 1. Clone the Repository
```bash
git clone https://github.com/tgasla/MLSysOps-VM-Management-Agent.git
cd MLSysOps-VM-Management-Agent
```

### 2. Create and Activate Virtual Environment

**Linux / macOS:**

```Bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```Bash
pip install -r requirements.txt
```

## 🚀 Quick Start
To verify the agent is working, simply run the demo script. This will automatically check for test scenarios (and generate them if missing) and run the agent against them.

```Bash
python demo.py
```

**Output Example:**

```Plaintext
--- 🧪 Testing Scenario: scenario_2.json ---
📥 Input Job Req: 8 cores
🤖 Raw Action:    [1 3 2 2]
✨ Action: Create VM
   -> Location: Host 3
   -> VM Type:  Large (ID: 2)
```

## 💻 Python Usage Guide
If you want to integrate this agent into your own application, here is the standard workflow:

```Python
import json
from src.inference_engine import MLSysOpsVMManagementAgent
from src.infra_state_serializer import InfraStateSerializer
from src.action_interpreter import ActionInterpreter

# 1. Initialize Components
# (Paths are relative to where you run the script)
config_path = "model/model_config.json"
model_path = "model/vm_management_agent.onnx"

agent = MLSysOpsVMManagementAgent(model_path, config_path)
serializer = InfraStateSerializer(config_path)
interpreter = ActionInterpreter(config_path)

# 2. Load Infrastructure State
# You can pass a dictionary or a file path
with open("scenario_1.json", "r") as f:
    state_data = json.load(f)

# 3. Prepare Inputs
# Serialize the complex tree structure into the model's expected vector
infra_vector = serializer.serialize(state_data)
# Get the pending job requirements (scalar)
job_req = state_data.get("total_job_cores_waiting", 0)

# 4. Predict
# The agent returns a raw discrete vector (e.g., [1, 12, 0, 2])
raw_action = agent.predict(infra_vector, job_req)

# 5. Interpret
# Convert raw numbers into a meaningful string
explanation = interpreter.humanify(raw_action)

print(f"Agent Recommendation: {explanation}")
```

## 🧪 Test Scenarios
The generate_scenarios.py script creates three distinct situations to test the AI's decision-making:

- **Scenario 1:** 32 Hosts (Empty) + 0 Waiting Jobs.

    - Expectation: Do Nothing.

- **Scenario 2:** 8 Hosts (Empty) + 8 Cores Waiting.

    - Expectation: Create a VM (likely Large) on any available host.

- **Scenario 3:** 16 Hosts (Populated with VMs) + 0 Waiting Jobs.

    - Expectation: Destroy a VM.

## ⚙️ Configuration & Model Card
The file `model/model_config.json` serves as the **Model Card**. It defines the exact input/output specifications and schema the model was trained on.

**Important:** You are not expected to change this file. The ONNX model's weights are permanently tied to these dimensions and definitions.

- `vector_length`: 801 (The fixed input array size).

- `action_decoding`: Maps the model's integer outputs to human-readable names (e.g., ID 0 -> "Small", ID 2 -> "Large").

- `hardware_definitions`: Defines the VM types/flavors the model learned to manage.

## 🇪🇺 Acknowledgments & Funding

This repository was developed by **University College Dublin (UCD)** as part of the **MLSysOps** project.

The MLSysOps consortium consists of **12 European partners** across academia and industry, working together to optimize AI-driven operations in the Cloud-Edge Continuum.

This project has received funding from the European Union’s Horizon Europe research and innovation programme under grant agreement **No 101092912**.

Learn more at [mlsysops.eu](https://mlsysops.eu)

<p align="left">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg" alt="EU Flag" width="100"/>
</p>
