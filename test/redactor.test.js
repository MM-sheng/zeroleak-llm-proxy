import assert from "node:assert/strict";
import test from "node:test";
import { redactJson, redactText, restoreJson, restoreText } from "../src/redactor.js";

test("redacts and restores emails and OpenAI keys", () => {
  const input = "Email alice@example.com with key sk-proj-abcdefghijklmnopqrstuvwxyz";
  const { redacted, replacements } = redactText(input);

  assert.equal(redacted, "Email [EMAIL_1] with key [OPENAI_KEY_1]");
  assert.equal(restoreText(redacted, replacements), input);
});

test("redacts nested JSON values", () => {
  const request = {
    model: "gpt-4o-mini",
    messages: [
      {
        role: "user",
        content: "postgres://user:pass@localhost:5432/app belongs to bob@example.com"
      }
    ]
  };

  const { redacted, replacements } = redactJson(request);

  assert.equal(
    redacted.messages[0].content,
    "[DATABASE_URL_1] belongs to [EMAIL_1]"
  );
  assert.deepEqual(restoreJson(redacted, replacements), request);
});

test("redacts private keys across lines", () => {
  const input = [
    "-----BEGIN PRIVATE KEY-----",
    "abc123",
    "-----END PRIVATE KEY-----"
  ].join("\n");

  const { redacted, replacements } = redactText(input);

  assert.equal(redacted, "[PRIVATE_KEY_1]");
  assert.equal(replacements["[PRIVATE_KEY_1]"], input);
});

