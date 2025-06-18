from tutor import hooks

# Plugin configuration
config = {
    "defaults": {
        "LLM_OAUTH_CLIENT_ID": "n9svQOtyYCkUZLLvPgH1LpEMuSynpO7VMSVeoFl5",
        "LLM_OAUTH_CLIENT_SECRET": "HuGrd4T9qmCPvZxkvcHehLYrn4mnYrRAyoN9VHb9ZqNM9aRY3msrrsUX5cQ0gyQR0pyWxz44zXKGHNGXQVxUwnRLdYxrGcaN6xOpf0ia5cAn2J8yUBi2HbikyJqA8cUG",
        "LLM_SERVICE_HOST": "localhost",
        "LLM_SERVICE_PORT": "8000",
    }
}

# Add configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"LLM_{key}", value) for key, value in config["defaults"].items()]
)

# Add configuration to the LMS
hooks.Filters.ENV_TEMPLATE_VARIABLES.add_items(
    [
        ("LLM_OAUTH_CLIENT_ID", "{{ LLM_OAUTH_CLIENT_ID }}"),
        ("LLM_OAUTH_CLIENT_SECRET", "{{ LLM_OAUTH_CLIENT_SECRET }}"),
        ("LLM_SERVICE_HOST", "{{ LLM_SERVICE_HOST }}"),
        ("LLM_SERVICE_PORT", "{{ LLM_SERVICE_PORT }}"),
    ]
) 