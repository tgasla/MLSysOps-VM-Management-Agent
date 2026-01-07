import json
import numpy as np

class ActionInterpreter:
    def __init__(self, config_path="model_config.json"):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # 1. Parse VM Names from 'action_decoding'
        # Your JSON structure: "action_decoding": { "vm_type_id": { "0": "Small", "1": "Medium" ... } }
        raw_map = config.get('action_decoding', {}).get('vm_type_id', {})
        
        self.vm_types_map = {}
        
        for type_id_str, name in raw_map.items():
            # JSON keys are strings ("0"), model gives integers (0)
            # We map int -> string (e.g., 0 -> "Small")
            try:
                type_id = int(type_id_str)
                self.vm_types_map[type_id] = name
            except ValueError:
                continue

    def humanify(self, action_vector):
        """
        Translates the model's action vector into a human-readable string.
        Vector Layout: [Action_Type, Host_ID, VM_ID, VM_Type_ID]
        """
        # Ensure we are working with a flat list/array
        if hasattr(action_vector, 'flatten'):
            action_vector = action_vector.flatten()
            
        action_type = int(action_vector[0])
        
        # --- CASE 0: DO NOTHING ---
        if action_type == 0:
            return "Action: Do Nothing"

        # --- CASE 1: CREATE VM ---
        elif action_type == 1:
            # Layout: [1, Host_ID, (Ignore), VM_Type_ID]
            host_id = int(action_vector[1])
            vm_type_id = int(action_vector[3])
            
            # Lookup directly using the integer ID
            vm_name = self.vm_types_map.get(vm_type_id, f"Unknown-Type-{vm_type_id}")
            
            return (f"Action: Create VM\n"
                    f"   -> Location: Host {host_id}\n"
                    f"   -> VM Type:  {vm_name}")

        # --- CASE 2: DESTROY VM ---
        elif action_type == 2:
            # Layout: [2, (Ignore), VM_ID, (Ignore)]
            vm_id = int(action_vector[2])
            
            return (f"Action: Destroy VM\n"
                    f"   -> Target: VM ID {vm_id}")

        # --- UNKNOWN CASE ---
        else:
            return f"Unknown Action Type: {action_type}"