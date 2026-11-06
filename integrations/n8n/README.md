# n8n workflow

Optional. The bundled `worker` service already does this; use n8n if you prefer to see and edit the
schedule visually or chain in other tools (Slack ping when posts are waiting for review, a Google
Sheet of ideas, etc.).

1. In n8n, set environment variables `FACTORY_URL` (e.g. `http://app:8000`) and `DASHBOARD_TOKEN`.
2. Import `content-factory-workflow.json` and change the brand slug in the "Daily run" node.
3. Add a notification node after "Count posts waiting for review" if you want a ping.

Approving posts stays a human step in the dashboard; there's deliberately no auto-approve node.
