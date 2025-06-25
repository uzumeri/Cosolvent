# 🔁 NGINX Reverse Proxy Gateway

This service acts as the central **API Gateway** for all microservices in the project. It handles **routing**, **security**, **rate limiting**, **basic caching**, and **log management**, allowing internal services to remain inaccessible from outside while still reachable via clean public routes.

---

## 📦 Directory Structure

```

reverse\_proxy/
├── nginx.conf          # Main NGINX configuration file
└──certbot/            # TLS certificates (used only in production) not yet implemented
    ├── conf/
    └── www/


````

---

## 🌐 Exposed Routes

This proxy listens on `http://localhost` (port 80) and exposes public endpoints like:

| Route Prefix              | Proxies To                         | Status     |
|---------------------------|------------------------------------|------------|
| `/asset/`                 | `asset_service:8002`               | ✅ Active  |
| `/industry-context/`      | `industry_context_service:8004`    | ✅ Active  |
| `/llm/`                   | `llm_orchestration_service:8000`   | ✅ Active  |
| `/profile-gen/`           | `profile_generation_service:8007`  | ✅ Active  |
| `/profile-manage/`        | `profile_management_service:8003`  | ✅ Active  |
| *(others)*                | *(see below for adding more)*      | 💤 Pending |

---

## 🛠️ How to Add a New Microservice

To route requests to a new service:

### 1. Define an Upstream

Add this block under `http {}` in `nginx.conf`:

```nginx
upstream <your_service_name> {
    server <docker_service_name>:<internal_port>;
}
````

Example:

```nginx
upstream user_management_service {
    server user_management_service:8011;
}
```

---

### 2. Add a Location Block

Inside the `server {}` block:

```nginx
location /<route-prefix>/ {
    proxy_pass http://<your_service_name>/;

    # Optional: enable rate limiting
    limit_req zone=api_limit burst=20 nodelay;

    # Optional: timeouts ( realise on /healthz endpoint on the services)
    proxy_connect_timeout 5s;
    proxy_send_timeout 10s;
    proxy_read_timeout 10s;

    # Optional: cache
    proxy_cache api_cache;
    proxy_cache_valid 200 302 10m;
    proxy_cache_valid 404 1m;
}
```

Example:

```nginx
location /user/ {
    proxy_pass http://user_management_service/;
}
```

---

### 3. Restart the Proxy

After updating `nginx.conf`, rebuild or restart the reverse proxy:

```bash
docker compose restart reverse_proxy
```

---

## 🧪 Local Development Notes

* Internal services should **NOT expose `ports:`** unless needed for debugging.
* All traffic should flow through the reverse proxy: `http://localhost/<route>/`
* Use `docker logs reverse_proxy` to inspect traffic and errors.

---

## 🛡️ Production Features Included

* ✅ **Rate Limiting** (`10 req/sec` per IP)
* ✅ **Security Headers** (XSS, Content-Type, Frame-Options, etc.)
* ✅ **Timeouts** (connect/read/send)
* ✅ **Caching** (200/302/404 responses)
* ✅ **Gzip Compression**
* ✅ **Access/Error Logging** (stdout or persisted in `reverse_proxy/logs/`)
* ✅ **Service Isolation** (no direct host access to internal services)

---

## 🔐 TLS (Production Only) setup required

To enable HTTPS with Let's Encrypt:

* Create and setup `prod.nginx.conf` instead of `nginx.conf`
* Make sure domain points to the server and ports 80/443 are open

---
