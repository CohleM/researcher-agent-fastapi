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

## NGINX CONF

Don't forget to add X-Forwarded-\* headers,
server {
listen 443 ssl; # managed by Certbot
server_name backend.okprofessor.com;

    ssl_certificate /etc/letsencrypt/live/backend.okprofessor.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/backend.okprofessor.com/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

    location / {
        proxy_pass http://localhost:8000;
          proxy_buffering off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
    }

    # Add other location blocks or configurations as needed

    error_page 404 /404.html;
    location = /404.html {
        root /usr/share/nginx/html;
        internal;
    }

    # Other error pages and configurations can be added as needed

}

server {
listen 80;
server_name backend.okprofessor.com;

    return 301 https://$host$request_uri;

}
