## Environment variables are not stored in the image itself.

Override the env_file specified in our docker compose usign this --env-file cli
docker compose --env-file ./config/.env.dev up
