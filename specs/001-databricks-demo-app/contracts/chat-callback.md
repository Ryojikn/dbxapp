# Contract: Chat Panel Callback

**Type**: Dash callback (server-side Python function)  
**Defined in**: `callbacks.py → handle_chat_submit()`

---

## Trigger

| Dash Input | Component ID | Property | Fires when |
|------------|-------------|----------|------------|
| User message | `chat-input` | `n_submit` or `n_clicks` on send button | User presses Enter or clicks Send |

---

## Inputs

| Name | Component ID | Property | Description |
|------|-------------|----------|-------------|
| `question` | `chat-input` | `value` | Raw text the user typed (1–500 chars) |
| `chat_history` | `chat-store` | `data` | `list[dict]` — existing `{role, content}` pairs from `dcc.Store` |

## Outputs

| Name | Component ID | Property | Description |
|------|-------------|----------|-------------|
| `updated_history` | `chat-store` | `data` | Appended history with new question + answer pair |
| `rendered_messages` | `chat-messages` | `children` | List of `html.Div` chat bubbles to render |
| `cleared_input` | `chat-input` | `value` | Returns `""` to clear the input box |

---

## Processing Contract

```
match_chat_rule(question, CHAT_RULES) → rule

if rule.is_anomaly_rule:
    response = render_anomaly_response(rule, KPI_SUMMARY)
elif DATABRICKS_SERVING_ENDPOINT is set AND DATABRICKS_TOKEN is set:
    response = call_model_serving(question, chat_history, KPI_SUMMARY)
    if call fails (timeout / HTTP error):
        response = render_template_response(rule, KPI_SUMMARY)
else:
    response = render_template_response(rule, KPI_SUMMARY)

return append_to_history(chat_history, question, response)
```

---

## Chat History Schema

```json
[
  {"role": "user",      "content": "What is our total revenue?"},
  {"role": "assistant", "content": "As of March 31, total MTD revenue is $2,847,392 ..."}
]
```

Maximum history retained in `dcc.Store`: 20 turns (older turns dropped FIFO).

---

## Response Quality Rules

1. Every non-fallback response MUST include at least one number from `KPISummary` (e.g., revenue figure, percentage).
2. The anomaly response MUST name the date (March 18), the margin collapse (23% → 6%), the order reference (ORD-48821), and a next step.
3. The fallback response MUST NOT return an empty string — it returns a prompt to rephrase.

---

## Model Serving Call Format

When live LLM mode is active:

```
POST {DATABRICKS_HOST}/serving-endpoints/{DATABRICKS_SERVING_ENDPOINT}/invocations
Authorization: Bearer {DATABRICKS_TOKEN}
Content-Type: application/json

{
  "messages": [
    {
      "role": "system",
      "content": "You are a data analytics assistant for a retail e-commerce platform. Current metrics: Total MTD Revenue: $2,847,392 (+12% MoM). Total Orders: 18,429. Avg Order Value: $154.52. Top category: Electronics ($891,034, 31% of total). Fastest growing: Sports (+28% QoQ). Active anomalies: 1 — Electronics COGS spike on March 18 (margin 23%→6%, order ORD-48821). Answer concisely and reference these numbers."
    },
    ... (prior turns from chat_history),
    {
      "role": "user",
      "content": "{question}"
    }
  ],
  "max_tokens": 300,
  "temperature": 0.1
}
```

Expected response shape (OpenAI-compatible):
```json
{
  "choices": [{"message": {"role": "assistant", "content": "..."}}]
}
```

Timeout: 10 seconds. On timeout or non-2xx response, fall through to keyword-matched template response.
