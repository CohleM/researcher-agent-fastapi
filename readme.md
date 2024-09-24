### Researcher Agent

The agent is capable of generating detailed, factual, and unbiased research reports, with customizable options to focus on specific resources, outlines, and insights. Drawing inspiration from recent Plan-and-Solve and RAG papers, This agent tackles challenges related to speed, consistency, and reliability, providing enhanced stability and faster performance by utilizing parallelized agent tasks instead of traditional synchronous operations.


### Install the dependency

```bash
pip install -r requirements.txt
```

### Run the server

```bash
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```


### Docker implmentation on VPS (ignore if using it locally)

Environment variables are not stored in the image itself.
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
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
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

## NOTE

nginx by default doesn't allow request body's payload to be large so make changes to nginx config to allow large files.

Edit the conf file of nginx:

nano /etc/nginx/nginx.conf
Add a line in the http, server or location section:

client_max_body_size 100M;
Don't use MB it will not work, only the M!

Also do not forget to restart nginx:

systemctl restart nginx
