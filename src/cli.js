#!/usr/bin/env node
import { redactText } from "./redactor.js";

const input = process.argv.slice(2).join(" ");

if (!input) {
  console.error("Usage: zeroleak-redact \"text containing secrets\"");
  process.exit(1);
}

console.log(JSON.stringify(redactText(input), null, 2));

