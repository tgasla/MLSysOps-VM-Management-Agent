import numpy as np
import json

class InfraStateSerializer:
    def __init__(self, config_path="model/model_config.json"):
        """
        Initialize the serializer by reading the target vector length from config.
        """
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        # Dynamically read the length (e.g., 801)
        self.target_length = config['input_spec']['vector_length']

    def serialize(self, input_data):
        """
        Extracts 'infrastructure_state' from the full JSON and 
        returns the padded/truncated float vector.
        """
        # A. Handle File Path vs Dictionary
        if isinstance(input_data, str):
            with open(input_data, 'r') as f:
                full_json = json.load(f)
        else:
            full_json = input_data

        # B. Safety extraction
        if "infrastructure_state" in full_json:
            infra_data = full_json["infrastructure_state"]
        else:
            infra_data = full_json

        # --- Depth-First Search (DFS) Traversal ---
        stream = []
        
        # 1. Datacenter
        stream.append(infra_data.get('total_cores', 0))

        hosts = infra_data.get('hosts', [])
        hosts = sorted(hosts, key=lambda x: x.get('id', 0))
        stream.append(len(hosts))

        # 2. Hosts Loop
        for host in hosts:
            stream.append(host.get('cores', 0))
            
            vms = host.get('vms', [])
            vms = sorted(vms, key=lambda x: x.get('id', 0))
            stream.append(len(vms))

            # 3. VMs Loop
            for vm in vms:
                stream.append(vm.get('cores', 0))
                
                jobs = vm.get('jobs', [])
                jobs = sorted(jobs, key=lambda x: x.get('id', 0))
                stream.append(len(jobs))

                # 4. Jobs Loop
                for job in jobs:
                    stream.append(job.get('cores', 0))
                    stream.append(0) # Jobs have 0 children

        # --- Final Polish ---
        raw_vector = np.array(stream, dtype=np.float32)
        final_vector = np.zeros(self.target_length, dtype=np.float32)
        
        # Use self.target_length for clamping
        actual_len = min(len(raw_vector), self.target_length)
        final_vector[:actual_len] = raw_vector[:actual_len]

        return final_vector