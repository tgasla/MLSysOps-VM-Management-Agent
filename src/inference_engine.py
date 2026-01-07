import onnxruntime as ort
import numpy as np
import json
import os

class MLSysOpsVMManagementAgent:
    def __init__(self, model_path="model/vm_management_agent.onnx", config_path="model/model_config.json"):
        """
        Initializes the ONNX Inference Session.

        Args:
            model_path (str): Path to the .onnx model file.
            config_path (str): Path to the model_config.json file.
        """

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at: {model_path}")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config not found at: {config_path}")

        # 1. Load Configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_name = self.session.get_outputs()[0].name

    def predict(self, infr_state, job_cores_waiting):
        """
        Predicts the placement action for a given state.

        Args:
            infr_state (np.array): The vector representation of the infrastructure.
            job_cores_waiting (float/int): The normalized core requirement of the job.

        Returns:
            np.array: The selected action (node index).
        """
        # --- 1. SAFETY: Clip Job Cores (The Fix) ---
        # The model was trained with a max observation of 8. 
        # We must clip inputs to prevent "Out of Distribution" errors.
        
        # Load from config
        max_allowed_job_cores = self.config['input_spec']['max_job_cores']

        job_cores_waiting = min(job_cores_waiting, max_allowed_job_cores)

        # --- 2. Preprocess Inputs ---
        # Ensure batch dimension exists (add dimension at index 0 if missing)
        if infr_state.ndim == 1:
            infr_state = np.expand_dims(infr_state, axis=0)
        
        # Job Cores: Needs shape (1,) for a scalar input
        # We assume single inference, so we wrap the scalar in a 1D array
        job_input = np.array([job_cores_waiting], dtype=np.float32)

        # --- 3. Prepare Feed Dictionary ---
        inputs = {
            self.input_names[0]: infr_state.astype(np.float32),
            self.input_names[1]: job_input
        }

        # --- 4. Run Inference ---
        result = self.session.run([self.output_name], inputs)

        # Return the action (remove batch dim)
        return result[0][0].astype(int) # Get the first row [ActionType, Host, VM, Type]