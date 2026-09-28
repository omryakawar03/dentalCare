# AI assistant architecture

AI operates through authenticated, typed, allow-listed tools. It cannot receive database credentials, issue arbitrary SQL, or read complete patient charts by default. A tool validates user identity, organization and clinic grants, permission, arguments, and response fields; queries only the minimum data; writes an audit event; and returns structured facts with provenance.

Initial target tools: appointment search/slot lookup, authorized revenue aggregates, low-stock/expiry summaries, follow-up lists, and draft generation. Mutations return a preview and require explicit confirmation before the ordinary domain service is called. Tool/action IDs and confirmation state are persisted so retries cannot double-book or duplicate ledger entries.

AI may draft administrative communication or summarize authorized operational data. It must not independently diagnose, prescribe, alter records, or expose patient details to an unauthorized role. Dentist-supervised clinical decision support must clearly label uncertainty and source context. Minimize/redact prompts, configure retention, restrict provider/model selection, and allow the organization to disable AI. Never send full patient records unless a later approved workflow proves that context necessary.
