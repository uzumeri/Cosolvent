# Auth Service

This is a auth service that uses the [better-auth](https://github.com/Better-Auth/better-auth) library to handle authentication and authorization.

Navigate to http://localhost:8020/api/auth/reference to view the OpenAPI documentation for the API.

## creating an admin user

To create an admin user, run the following command:

first, exec to the docker service

```bash
    docker compose exec auth_service sh
```

then run the following command:

```bash
    pnpm run seed:admin
```

This will prompt you for the admin name, email, and password.
