# Deployment

Status: **F1 compose skeleton; not production-routed**

`docker-compose.yml` defines the minimal Inventory API + isolated PostgreSQL runtime shape.

## Security defaults

- API host publish is localhost-only: `127.0.0.1:${MSA_API_HOST_PORT:-8088}:8080`.
- PostgreSQL has no host port mapping and is reachable only on the internal Docker network.
- Real secrets must come from protected VPS runtime configuration; never commit `.env`.
- Cloudflare hostname routing is intentionally deferred until the API health endpoint is verified on the VPS.

## Validation target

Before any VPS deployment, run:

```bash
docker compose --env-file /path/to/protected/runtime.env -f deploy/docker-compose.yml config
```

F1 does not authorize inventory migrations, live-data import, Custom GPT Actions, or database canonical promotion.
