# Srichand advisor MCP server (HTTP). Build: docker build -t srichand-mcp .   Run: docker run -p 8787:8787 -e SRICHAND_MCP_TOKEN=... srichand-mcp
# The SQLite file is built at container START, not at image build: Bun's JIT segfaults under QEMU, so baking it in
# would break `docker build --platform linux/amd64` from an Apple Silicon Mac (App Runner / Lightsail need x86_64).
# No volume  -> a fresh DB every start; demo writes (orders, consents) are lost on restart.
# Volume at /app/db -> built once, then persisted across restarts.
FROM oven/bun:1
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --production
COPY db/schema.sql db/build.ts db/tables.ts ./db/
COPY db/seed ./db/seed
COPY mcp-server ./mcp-server
ENV PORT=8787
EXPOSE 8787
CMD ["sh", "-c", "[ -f db/srichand.db ] || bun run db/build.ts; exec bun run mcp-server/src/http.ts"]
