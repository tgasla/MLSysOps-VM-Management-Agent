import json

# Global Constants
HOST_CAPACITY = 16

def write_json(filename, hosts_data, waiting_cores):
    """
    Helper to calculate totals and write the file.
    """
    # Calculate DC Total based on SUM of all hosts' TOTAL capacity
    dc_total_capacity = sum(h['cores'] for h in hosts_data)

    full_state = {
        "infrastructure_state": {
            "datacenter_id": "test-cluster",
            "total_cores": dc_total_capacity,
            "hosts": hosts_data
        },
        "total_job_cores_waiting": waiting_cores
    }

    with open(filename, 'w') as f:
        json.dump(full_state, f, indent=4)
    print(f"✅ Generated {filename} | Hosts: {len(hosts_data)} | Waiting: {waiting_cores}")


def create_scenario_1():
    """
    Scenario 1: 32 Hosts, Empty, 0 Waiting.
    """
    num_hosts = 32
    hosts_data = []

    for i in range(num_hosts):
        hosts_data.append({
            "id": i,
            "cores": HOST_CAPACITY, # Always Total
            "vms": []
        })

    write_json("scenario_1.json", hosts_data, waiting_cores=0)


def create_scenario_2():
    """
    Scenario 2: 8 Hosts ONLY, Empty, 8 Waiting.
    """
    num_hosts = 8
    hosts_data = []

    for i in range(num_hosts):
        hosts_data.append({
            "id": i,
            "cores": HOST_CAPACITY, # Always Total
            "vms": []
        })

    write_json("scenario_2.json", hosts_data, waiting_cores=8)


def create_scenario_3():
    """
    Scenario 3: 16 Hosts, At least 8 VMs (No jobs inside), 0 Waiting.
    """
    num_hosts = 16
    hosts_data = []

    for i in range(num_hosts):
        # Strategy: Place 1 VM on every host to ensure we have 16 VMs total.
        # VM Specs: Random/Fixed size (e.g., 8 cores)
        
        vm_entry = {
            "id": i,      # Unique ID
            "cores": 8,         # VM Size (Total allocated)
            "jobs": []          # "No jobs at all"
        }

        hosts_data.append({
            "id": i,
            "cores": HOST_CAPACITY, # Always Total (16)
            "vms": [vm_entry]
        })

    write_json("scenario_3.json", hosts_data, waiting_cores=0)