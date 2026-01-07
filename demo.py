import os
import json
import numpy as np

# Import your custom modules
from src.inference_engine import MLSysOpsVMManagementAgent
from src.infra_state_serializer import InfraStateSerializer
from src.action_interpreter import ActionInterpreter

import generate_scenarios

# --- Configuration ---
MODEL_PATH = "model/vm_management_agent.onnx"
CONFIG_PATH = "model/model_config.json"
SCENARIOS = ["scenario_1.json", "scenario_2.json", "scenario_3.json"]

def create_scenarios():
    """
    Generates scenarios.
    """
    
    generate_scenarios.create_scenario_1()
    generate_scenarios.create_scenario_2()
    generate_scenarios.create_scenario_3()
    print("✅ Scenarios generated successfully.\n")

def run_test_case(scenario_file, agent, serializer, interpreter):
    print(f"--- 🧪 Testing Scenario: {scenario_file} ---")
    
    # 1. Load JSON State
    try:
        with open(scenario_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Could not load {scenario_file}")
        return

    # 2. Serialize Inputs (Using the object instance now)
    infra_vector = serializer.serialize(data)
    
    # Get the job requirement
    job_req = data.get("total_job_cores_waiting", 0)

    # 3. Get Action
    action = agent.predict(infra_vector, job_req)

    # 4. Humanify Action
    human_readable_action = interpreter.humanify(action)

    # 5. Output Results
    print(f"📥 Input Job Req: {job_req} cores")
    print(f"🤖 Raw Action:    {action}")
    print(f"{human_readable_action}\n")

def main():
    # 1.  Generate Scenarios
    create_scenarios()

    # 2. Initialize Components
    print("🚀 Initializing Agent, Serializer, and Interpreter...")
    
    # Initialize all three components with the config path
    agent = MLSysOpsVMManagementAgent(MODEL_PATH, CONFIG_PATH)
    serializer = InfraStateSerializer(CONFIG_PATH)  # <--- Now instantiated!
    interpreter = ActionInterpreter(CONFIG_PATH)
    
    print("✅ System Ready.\n")

    # 3. Run All Tests
    for scenario in SCENARIOS:
        run_test_case(scenario, agent, serializer, interpreter)

if __name__ == "__main__":
    main()