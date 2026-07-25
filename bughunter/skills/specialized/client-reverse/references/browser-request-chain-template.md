# Browser Request Chain Template

Use this template for browser-side sign, token, anti-bot, worker, wasm, cookie-hop, and replay tasks.

## Template

```markdown
# Browser request chain record

## Basic information

- Target page:
- Target request:
- Target field:
- Trigger action:
- Current stage:locate / recover / runtime / validation
- Current status:🟡 in progress / ✅ Closed loop / ⛔ block
- Target:
- constraint:

## Samples and phenomena

- Normal sample:
- Risk control status sample:
- Browser phenomenon:
- Local phenomena:
- Current differences:

## Request chain main table

| project | content |
| --- | --- |
| writer |  |
| builder |  |
| entry |  |
| source |  |
| upstream dependency |  |
| state carrier |  |
| Risk control bifurcation point |  |
| current conclusion |  |

## key evidence

| Evidence type | Location/point | content | in conclusion |
| --- | --- | --- | --- |
| Request sample |  |  |  |
| call stack |  |  |  |
| breakpoint/Hook |  |  |  |
| middle value |  |  |  |
| Cookie/Storage |  |  |  |

## stage supplement

### Locate Replenish

- Sink:
- Real writing point:
- Upstream request:
- normal state / Risk control status distinction:

### Recover Replenish

- Mask type:
- Current recovery level:A / B / C
- Contract restored:
- Still not restored notch:

### Runtime Replenish

- Missing objects:
- Missing status:
- Fixed source:
- First point of disagreement:
- Risk control / Anti-debugging:

### Validation Replenish

| checkpoint | Browser side | local/recovery side | result | evidence | gap |
| --- | --- | --- | --- | --- | --- |
| checkpoint1 |  |  |  |  |  |

## Burp replay baseline

- Method:
- Path:
- Query:
- Headers:
- Body:
- Required fields:
- Mutable fields:
- Prerequisite status:

## Stage Handoff

--- Stage Handoff ---
From:
To:
Proven:
Open:
Invalidated:

## Next step

- Next action:
- Expected output:
- Choking point:
```

## Minimum Required Fields

Even in a compact record, keep:

- target page and target request
- current stage
- `writer / builder / entry / source`
- one real request sample
- one concrete evidence row
- Burp replay baseline or explicit blocker
