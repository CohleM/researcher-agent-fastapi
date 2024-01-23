## Environment variables are not stored in the image itself.

Override the env_file specified in our docker compose usign this --env-file cli
docker compose --env-file ./config/.env.dev up

## backup postgres data

1. STOP the container with docker stop container name
2. backup from server
   docker run --rm \
    --user root \
    --volumes-from pg_container \
    -v /tmp/db-bkp:/backup \
    ubuntu tar cvf /backup/db.tar /var/lib/postgresql/data

3. restore in local
   docker run --rm \
    --user root \
    --volumes-from 52c93f1d58a9 \
    -v /Users/cohlem/Projects/Fastapi/db-bkp:/backup \
    ubuntu bash -c "cd /var && tar xvf /backup/db.tar --strip 1"
