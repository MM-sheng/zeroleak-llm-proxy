import http from "node:http";
import { loadEnv } from "./load-env.js";
import { redactJson, restoreJson } from "./redactor.js";

loadEnv();

const port = Number(process.env.PORT ?? 8787);
const upstreamBaseUrl = process.env.UPSTREAM_BASE_URL ?? "https://api.openai.com";
const upstreamApiKey = process.env.UPSTREAM_API_KEY;

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "GET" && req.url === "/health") {
      return sendJson(res, 200, { ok: true });
    }

    if (req.method === "POST" && req.url === "/v1/chat/completions") {
      const body = await readJson(req);
      const { redacted, replacements } = redactJson(body);
      const upstreamResponse = await forwardChatCompletion(redacted, req.headers);
      const restored = restoreJson(upstreamResponse, replacements);

      return sendJson(res, 200, {
        ...restored,
        zeroleak: {
          redacted_count: Object.keys(replacements).length,
          redacted_types: summarizeTypes(replacements)
        }
      });
    }

    return sendJson(res, 404, { error: "Not found" });
  } catch (error) {
    return sendJson(res, error.statusCode ?? 500, {
      error: error.message ?? "Unexpected error"
    });
  }
});

async function forwardChatCompletion(body, headers) {
  if (!upstreamApiKey) {
    throw Object.assign(
      new Error("UPSTREAM_API_KEY is required to forward requests"),
      { statusCode: 500 }
    );
  }

  const response = await fetch(`${upstreamBaseUrl}/v1/chat/completions`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${upstreamApiKey}`,
      "user-agent": headers["user-agent"] ?? "zeroleak-llm-proxy"
    },
    body: JSON.stringify(body)
  });

  const text = await response.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    throw Object.assign(new Error(`Upstream returned non-JSON response: ${text}`), {
      statusCode: 502
    });
  }

  if (!response.ok) {
    throw Object.assign(new Error(json.error?.message ?? "Upstream request failed"), {
      statusCode: response.status
    });
  }

  return json;
}

function summarizeTypes(replacements) {
  const counts = {};
  for (const placeholder of Object.keys(replacements)) {
    const match = placeholder.match(/^\[([A-Z_]+)_\d+\]$/);
    if (!match) continue;
    counts[match[1]] = (counts[match[1]] ?? 0) + 1;
  }
  return counts;
}

async function readJson(req) {
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }

  const raw = Buffer.concat(chunks).toString("utf8");
  if (!raw) {
    return {};
  }

  try {
    return JSON.parse(raw);
  } catch {
    throw Object.assign(new Error("Invalid JSON body"), { statusCode: 400 });
  }
}

function sendJson(res, statusCode, data) {
  res.writeHead(statusCode, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store"
  });
  res.end(JSON.stringify(data, null, 2));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  server.listen(port, () => {
    console.log(`ZeroLeak LLM Proxy listening on http://localhost:${port}`);
  });
}

export { server };
