from tutor import hooks

# Add OAuth2 configuration to LMS
hooks.Filters.ENV_TEMPLATE_VARIABLES.add_items(
    [
        ("OAUTH2_PROVIDER", {
            "OAUTH2_PROVIDER_APPLICATION_MODEL": "oauth2_provider.Application",
            "OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL": "oauth2_provider.AccessToken",
            "OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL": "oauth2_provider.RefreshToken",
            "OAUTH2_PROVIDER_GRANT_MODEL": "oauth2_provider.Grant",
            "OAUTH2_PROVIDER_ID_TOKEN_MODEL": "oauth2_provider.IDToken",
            "OAUTH2_PROVIDER_APPLICATION_MODEL": "oauth2_provider.Application",
        }),
    ]
)

# Add WebSocket configuration
hooks.Filters.ENV_TEMPLATE_VARIABLES.add_items(
    [
        ("CHANNEL_LAYERS", {
            "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {
                    "hosts": [("redis", 6379)],
                },
            },
        }),
    ]
)

# Add static files configuration
hooks.Filters.ENV_TEMPLATE_VARIABLES.add_items(
    [
        ("STATICFILES_DIRS", [
            ("{{ tutor_llm_root }}/static"),
        ]),
    ]
) 