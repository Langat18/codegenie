node system {
    has name = "system";
    has created = 0;
}

# Include the agents package
import:jac from agents;

# Minimal init walker that creates a system node and spawns the supervisor walker
walker init {
    can start with entry {
        spawn here ++> node::system;
        # spawn the main supervisor walker from agents
        spawn here walker::CodeGenius;
    }
}

# Entry convenience
with entry {
    root_node = spawn here ++> node::system;
    spawn root_node walker::CodeGenius;
}