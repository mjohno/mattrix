# Flow: <name>

## Graph

```mermaid
flowchart TD
  FSTA_001([FSTA-001: Start]) -->|<start criterion>| FACT_001[FACT-001: <activity>]
  FACT_001 -->|<completion criterion>| FDEC_001{FDEC-001: <decision question>}
  FDEC_001 -->|<pass criterion>| FEND_001([FEND-001: Complete])
  FDEC_001 -->|<failure criterion>| FACT_002[FACT-002: <corrective activity>]
  FACT_002 -->|<correction criterion>| FDEC_001
```

## Nodes

### `FACT-001`

<activity description and completion criteria>

### `FDEC-001`

<decision question and outgoing-path criteria>

### `FACT-002`

<corrective activity description and completion criteria>
