# URL Checker - Broken Training Mode

This project is intentionally misconfigured so you can practice fixing real deployment issues from Part 1 to Part 5.

Important:
- This is not production-ready.
- Several settings are intentionally wrong.
- Fix one part at a time in order.

## Suggested Fix Order

1. Part 1 - Localhost vs Production
2. Part 2 - Docker
3. Part 3 - Cloud deployment (Railway/Render)
4. Part 4 - API gateway hardening
5. Part 5 - Scaling and reliability

## Quick Start (Expected To Fail Initially)

Run:

docker compose up -d --build

Then test:

curl -i http://localhost:8080/health

## Expected Symptoms

- Build and runtime commands may fail at first.
- Nginx may return 502.
- Health/readiness behavior is not trustworthy.
- Security controls are weak or bypassable.
- Session/history behavior is not truly stateless.

## Your Mission

- Make this app production-ready.
- Keep notes for each fix and map them to Part 1-5.
- Deploy to a cloud provider after local fixes pass.
