# Data Layout Structure Prototype: <Name>

## Decision
What decision will this data layout inform?

## Assumption
What data shape, relationship, import/export, or downstream usability assumption is being tested?

## Audience / Context
- Producers:
- Consumers:
- Lifecycle stage:
- Usage context:

## Scope
What data is included?

## Omitted
What storage, migration, performance, compliance, or production concerns are intentionally excluded?

## Entities / Records
| Entity | Purpose | Producer | Consumer |
|--------|---------|----------|----------|
|  |  |  |  |

## Field Definitions
| Field | Type | Required? | Meaning | Example | Notes / Constraints |
|-------|------|-----------|---------|---------|---------------------|
| id | string | yes | Stable identifier | item_123 |  |
|  |  |  |  |  |  |

## Relationships / Keys
- Primary key:
- Foreign keys or references:
- Grouping or ordering rules:
- Cardinality assumptions:

## Sample Data
```json
{
  "id": "item_123",
  "name": "Example item",
  "status": "draft"
}
```

## Example Consumer Operations
- Render:
- Query/filter:
- Import/export:
- Output/map:

## Privacy / Sensitivity Notes
- 

## Validation Signals
- 

## Failure Signals
- 

## Next Decision
What will be decided after reviewing the layout and sample data?
