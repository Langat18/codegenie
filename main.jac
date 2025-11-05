"""
Codebase Genius - Main Entry Point
Modular architecture with separate files for better organization
"""

import:py from config.llm_config {get_llm_instance};

# Initialize LLM globally
glob llm = get_llm_instance();

# Import all modules
include:jac "nodes/__init__.jac";
include:jac "agents/__init__.jac";
include:jac "api/__init__.jac";

with entry {
    print("\n" + "="*70);
    print("  CODEBASE GENIUS - Agentic Documentation System");
    print("="*70);
    print("\nServer running. Available endpoints:");
    print("  • POST /walker/generate_docs");
    print("  • POST /walker/quick_analyze");
    print("\nExample:");
    print('  curl -X POST http://localhost:8000/walker/generate_docs \\');
    print('    -H "Content-Type: application/json" \\');
    print('    -d \'{"repo_url": "https://github.com/pallets/click"}\'');
    print("\n" + "="*70 + "\n");
}
