Notes:
- This service uses Postgres + pgvector only. No MongoDB/Pinecone.
- If you see stale entries in pnpm-lock.yaml for mongodb or pinecone, delete the lockfile and run `pnpm install` to regenerate.
```
npm install
npm run dev
```

```
open http://localhost:3000
```
