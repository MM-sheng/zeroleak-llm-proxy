export const patterns = [
  {
    label: "PRIVATE_KEY",
    regex: /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/g
  },
  {
    label: "OPENAI_KEY",
    regex: /\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b/g
  },
  {
    label: "AWS_ACCESS_KEY",
    regex: /\bAKIA[0-9A-Z]{16}\b/g
  },
  {
    label: "JWT",
    regex: /\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g
  },
  {
    label: "DATABASE_URL",
    regex: /\b(?:postgres|postgresql|mysql|mongodb|redis):\/\/[^\s"'<>]+/gi
  },
  {
    label: "EMAIL",
    regex: /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi
  },
  {
    label: "US_SSN",
    regex: /\b\d{3}-\d{2}-\d{4}\b/g
  },
  {
    label: "CN_ID",
    regex: /\b[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b/g
  },
  {
    label: "PHONE",
    regex: /(?<!\w)(?:\+?\d[\d .-]{8,}\d)(?!\w)/g
  }
];

