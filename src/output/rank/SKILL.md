---
name: rank
description: Use when a collection of information needs an ordered priority based on user-defined criteria.
metadata:
  type: skill
  category: output
---

# rank

Goal: Produce a transparent ordered priority for a collection of items using stated qualitative or quantitative criteria.
Non-Goals: Discovering the collection, inventing missing criteria, making implementation changes, or executing the selected items.
Use-When: A collection of information needs ranking or prioritization based on user-defined scoring criteria.

## 0. Prerequisites
- A collection of items to compare.
- Criteria sufficient to distinguish their priority; weights are optional.

## 1. Inputs
- Items to rank.
- Ranking criteria, including any weights, constraints, or required tie-breakers.
- Optional source references supporting item attributes or scores.

## 2. Processes
1. Confirm the items and criteria; ask for missing material criteria rather than inventing them.
2. Remove information irrelevant to the stated criteria and record assumptions that materially affect the result.
3. Score or assess each item against the criteria, respecting explicit weights or listed priority order.
4. Resolve ties using the stated tie-breaker; otherwise report the tie rather than implying precision.
5. Order the items and explain material tradeoffs, uncertainty, and supporting evidence.

## 3. Outputs
- Ordered items, highest priority first, with scores or qualitative rationale.
- Criteria, weights, assumptions, ties, and material tradeoffs used to produce the order.
- A chat result by default, or a written artifact when the caller specifies an output path.

## 4. Next Steps
- `interface/plan` with `draft` — turn selected priorities into gap-closing work.
- `map/step` — execute approved work in priority order.
- `output/check` — validate whether the ranking followed the supplied criteria.

## 5. Examples

### Example 1: Ranking solution concepts

**Prompt:** "Rank these solution concepts by feasibility, cost, and potential impact, with feasibility most important."
**Outcome:** An ordered list with the applied criteria, rationale for each position, and any unresolved ties or assumptions.
