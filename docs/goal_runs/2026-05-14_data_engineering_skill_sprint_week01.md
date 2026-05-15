# Data Engineering Skill Sprint — Run Log

Date: 2026-05-14  
Sprint week: 1 (SQL foundations)  
Time budget: 10-15h/week target

## Next sprint step picked

Week 1: JOINs, CTEs, aggregation, NULL handling (SQLite on retail pipeline DB).

## Skill tasks (2)

1) **SQL foundations reps (90-120 min)**
   - Run the Week 1 query pack against `data/processed/kpi_dashboard.sqlite`.
   - For each query: sanity-check row counts + 1 edge-case note (NULLs/duplicates/grain).

2) **KPI reasoning drill (60-90 min)**
   - Pick 3 KPIs from the marts (`mart_monthly_revenue`, `mart_product_performance`, `mart_customer_segments`).
   - For each KPI: write (a) definition (grain + filters), (b) “what can break”, (c) 1 validation query.

## Mini deliverable (1)

- Query pack file: `docs/skill_sprint/week01_sql_foundations_query_pack.sql`
  - Output target: execute cleanly in SQLite; keep notes in comments.

## Interview questions (5) + answer guidance

1) **INNER vs LEFT JOIN: when does LEFT change results?**
   - Answer: LEFT keeps unmatched left rows; NULLs appear on right; filters on right table in WHERE can “undo” LEFT; move right-side filters to ON when needed.

2) **CTE vs subquery: any performance difference?**
   - Answer: logically same; some engines materialize CTEs; treat as readability tool; validate with EXPLAIN when performance matters.

3) **NULLs in aggregates: COUNT(*) vs COUNT(col) and SUM/AVG behavior?**
   - Answer: COUNT(*) counts rows; COUNT(col) ignores NULL; SUM/AVG ignore NULL (but return NULL if all NULL); use COALESCE for defaults.

4) **How do you avoid double-counting in joins?**
   - Answer: ensure correct grain; join on keys that preserve 1:1 or many:1; pre-aggregate; de-dup with DISTINCT only as last resort; validate with row-count checks.

5) **What is “grain” and why do you care?**
   - Answer: grain = what 1 row represents; mismatched grain causes duplication/wrong KPIs; define grain early (facts/dims) and enforce with PK-like checks.

## Weak-skill note (1)

- Likely weak spot: **join-grain debugging** (spotting hidden many-to-many + WHERE vs ON filter bugs). Drill with row-count diffs + “anti-join” checks.

