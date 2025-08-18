# Reverse Proxy

[← Services](./README.md) | [← Contents](../README.md)

Nginx-based reverse proxy that routes HTTP requests to individual microservices.

## Responsibilities
- Expose a single entry point and map paths to services.
- Handle basic concerns like timeouts and headers.

## Configuration
- See `src/services/reverse_proxy/nginx.conf` for route definitions.
- Update when adding or renaming services to keep paths consistent.

Prev: Search Service (./search_service.md) | Next: Frontend (../frontend.md)
