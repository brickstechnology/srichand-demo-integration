# Srichand advisor MCP server (HTTP). Build: docker build -t srichand-mcp .   Run: docker run -p 8787:8787 -e SRICHAND_MCP_TOKEN=... srichand-mcp
# The SQLite file lives inside the container: demo writes (orders, consents) are lost on redeploy — mount a volume at /app/db to keep them.
FROM oven/bun:1
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --production
COPY db/schema.sql db/build.ts ./db/
COPY db/seed ./db/seed
COPY mcp-server ./mcp-server
RUN bun run db/build.ts
ENV PORT=8787
EXPOSE 8787
CMD ["bun", "run", "mcp-server/src/http.ts"]
