Back end and API for banned-word related stuff. Definitely a work in progress.

The server supports an extremely basic form of authentication, which requires the `Authorization` header to match exactly what the server knows to be the API token of the bot. More permissive methods (mostly checking against discord to see if the user has the right permissions) will be coming soon.
