import { patterns } from "./patterns.js";

export function redactText(input) {
  if (typeof input !== "string" || input.length === 0) {
    return {
      redacted: input,
      replacements: {}
    };
  }

  let redacted = input;
  const replacements = {};
  const counters = new Map();

  for (const pattern of patterns) {
    redacted = redacted.replace(pattern.regex, (match) => {
      const next = (counters.get(pattern.label) ?? 0) + 1;
      counters.set(pattern.label, next);

      const placeholder = `[${pattern.label}_${next}]`;
      replacements[placeholder] = match;
      return placeholder;
    });
  }

  return { redacted, replacements };
}

export function restoreText(input, replacements) {
  if (typeof input !== "string" || input.length === 0) {
    return input;
  }

  let restored = input;
  for (const [placeholder, value] of Object.entries(replacements ?? {})) {
    restored = restored.split(placeholder).join(value);
  }

  return restored;
}

export function redactJson(value) {
  const replacements = {};
  const redacted = walk(value, (text) => {
    const result = redactText(text);
    Object.assign(replacements, result.replacements);
    return result.redacted;
  });

  return { redacted, replacements };
}

export function restoreJson(value, replacements) {
  return walk(value, (text) => restoreText(text, replacements));
}

function walk(value, transformText) {
  if (typeof value === "string") {
    return transformText(value);
  }

  if (Array.isArray(value)) {
    return value.map((item) => walk(item, transformText));
  }

  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, walk(item, transformText)])
    );
  }

  return value;
}

