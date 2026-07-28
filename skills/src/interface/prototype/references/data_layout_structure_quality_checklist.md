# Data Layout Structure Quality Checklist

Use this checklist when outlining, drafting, modifying, or reviewing a data layout structure prototype.

## Critical
- [ ] States the decision the data layout will inform.
- [ ] Names the data shape, relationship, import/export, or downstream usability assumption being tested.
- [ ] Identifies intended producers, consumers, and lifecycle context.
- [ ] Defines entities, records, fields, types, required/optional status, and meaning.
- [ ] Includes realistic sample data.
- [ ] Defines relationships, keys, constraints, or ordering rules when relevant.
- [ ] Notes privacy, sensitivity, retention, or compliance constraints if relevant.
- [ ] Defines validation signals, such as consumers being able to map, query, render, or transform the data.
- [ ] Defines failure signals, such as ambiguous field meaning, missing identifiers, or unusable nesting.
- [ ] Lists omitted storage, migration, or production concerns.

## Quality
- [ ] Uses the lowest-fidelity representation that can test the data decision.
- [ ] Avoids invented precision where the domain is uncertain.
- [ ] Keeps field names consistent and readable.
- [ ] Separates schema notes from sample data.
- [ ] Ends with a clear next decision.
