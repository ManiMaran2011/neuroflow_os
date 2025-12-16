def compute_paei_weights(user_input, agent_outputs):
    scores = {
        "producer": 1.0,
        "administrator": 1.0,
        "entrepreneur": 1.0,
        "integrator": 1.0
    }

    final_text = ""

    for agent_name, output in agent_outputs.items():
        if not output:
            continue
        final_text += f"{agent_name}: {output}\n"

    return final_text.strip()

