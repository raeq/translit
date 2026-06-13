# Output Encoders

Context-explicit **output encoders** — correct for a *specific* output sink, applied at the sink, exactly once.

These are deliberately **standalone terminal functions, not pipeline steps**: output encoding depends on the destination context (HTML element vs. attribute vs. URL component), which a context-free [pipeline](pipelines.md) cannot know. Baking an encoder into a pipeline invites double-encoding, wrong-context escaping, and storing pre-escaped text.

They do **not** make disarm an XSS/injection framework — they are narrow, context-pinned encoders, the explicit exception to disarm's ["not an output sanitizer"](https://github.com/raeq/disarm/blob/main/THREAT_MODEL.md) positioning. Run them at output, *after* (not instead of) the input-normalization layer.

## escape_html

::: disarm.escape_html

---

## percent_encode

::: disarm.percent_encode

### Component

::: disarm.Component
