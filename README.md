# Estrella 

## An Inferred, Progressively Adoptable Semantic Layer

This project introduces a new semantic layer that’s
primarily inferred from a
physical database schema, enabling automatic and intelligent interpretation
of database relationships. While a substantial amount of information can
be derived from the physical schema, our approach allows for
augmentation where needed, handling ambiguous cases, and progressive
enrichment over time using either yaml or as code.


## Served as a virtual database

Something that's novel about Estrella is the idea of exposing this
semantic layer primarily as a virtual database. This shows as one
very large table exposing essentially all of the columns in your semantic
layer. While you run very simple SQL against that large table,
Estrella transpiles this query into a more complex query against the
underlying physical schema. On top of this large table, Estrella exposes
a set of metadata tables with all the semantics
(metrics, dimensions, hierarchies, ...)

## REST too, or course

If the virtual database doesn't suit your need, a RESTful API is also
exposed....

Read on to understand the premises, proposed mechanics, implementation,
and how you can contribute to this innovative solution.

## Compiled 

Our engine makes inferences based on your physical schema, naming
conventions and enrichment as yaml or code, it "compiles" all this
to a static, deterministic model, that can be pushed to the file system
for source control (similar to how npm's `package-lock.json` is derived
from a more dynamic `package.json`) or to a `_meta` meta table in
a target database.

# Premises

## Premise #1 A lot can be inferred from a physical schema

Database schemas are full of semantics, and data modeling and naming
conventions augments these semantics even more. 

### Inferring joins

- if you have two tables in a given schema, and one of them has
  `customer_id` as its PRIMARY KEY  and the other table happens to
  have `customer_id`, it’s safe to infer you can join the two table on that PK
- even better, if a `FOREIGN KEY` constraint is defined, you can even more safely infer that the join stipulated in the physical layer is safe to use
- less clearly, if one table is called `customer` has an `id` column, and some other table has a `customer_id` you can pretty much guess that the [`customer.id](http://customer.id) = other_table.customer_id` is valid

### Inferring metrics

- looking at numerical column names, it may make sense to create some `SUM(amount)` `SUM(quantity)`

### Inferring other stuff?

- How do we store user-defined metrics?

## Premise #2 Even more can be inferred from a query corpus

[optional but interesting, maybe a V4 kinda thing] Interestingly, if you have a corpus of SQL as say a database log of user queries or other-bi-tools generate, those in theory could be parsed to infer patterns that answers:

- which tables can be joined and how
- which metrics are commonly used (look for aggregate expressions!)
- commonly used filters

The tool could have a feature something that reads through valid SQL and suggests augmentation of the semantic layer based on query pattern. Probably AI-based.

## Premise #3 A smart CLI could ask you to clarify ambiguous things

- not sure what to join on? ask the admin
- low confidence suggestions? ask the user

## Premise #4 You can enrich things over time

- Business metadata is not vital, and often takes a moment to settle, let’s put in pretty label, pretty description, fancy folders structures when we get there
- Hierarchies are nice but we can do without as we start
- Things like “List of Values”, informing how a dropdown for a given dimension should be populated for instance, are nice to haves, we don’t need this on day 0
- Aggregate awareness semantics aren’t vital
- …

# Proposition - Let’s build a semantic layer that’s mostly inferred from the physical schema, and can be progressively augmented over time.

## Proposed Mechanics - a virtual database

The main interface exposed to the user here is a virtual database that look likes a normal database. By default the API is SQL and a set of **virtual** data tables and metadata tables. Querying those tables transpiles the query to the more complex underlying physical model and/or the supporting metadata in memory 

### Inputs

- **a pointer to a database schema:** by default, this is all that’s needed to work, assume decent naming conventions and inferable schemas, this should work just fine by itself
- Augment it! extra metadata in the form of yaml files or DSL
    - joins (how individual schemas in the table should be joined)
    - contexts (inspired by Business Objects): define which joins can / cannot be used in combination.
    - metrics: them aggregate expressions
        - fancy stuff - V2 (not MVP)
            - metrics can refer to multiple columns from multiple tables, reference other metrics
            - meta-metrics can be defined, bookings can be defined on top of multiple tables `agg_bookings` and `fact_bookings`, and this engine knows how to pick the cheaper one to use
    - reusable filters
    - hierarchies as tuple of dims
    - hide tables/columns
    - folder structure defining how to expose objects

### Outputs - A set of Virtual Table

- `super`: A fat, wide virtual table that exposes ALL COLUMNS as one big table.
    - syntactic sugar! 🙂 `FROM *`:  `SELECT country_name, COUNT(DISTINCT customer_id) **FROM *** GROUP BY customer_name`
- `context.{context_name}` showing a subset of columns that can be joined together
- A virtual `meta` schema to
    - `meta.metrics`
    - `meta.objects`
    - `meta.dimensions`
    - `meta.hierarchies`

### Mechanics:

- When querying a virtual table like `super` , we read the SQL and transpile it into a proper plan
- When querying metadata, serve the model straight from memory

### “Compiling” + caching

Ok so there’s a lot of inferences that happen based on the physical schema, but probably should be inferred by the engine on the fly at each query. It feels like we need a step to combine the inferences based on the physical model and the augmentation and mix them things into a materialized, serialized, cached, versioned semantic layer.

Maybe things are pushed into a private `_meta` table in the physical schema itself, stamped, versioned, accessible, …

```sql
CREATE TABLE _meta AS (
  git_sha STRING,
  object_type STRING,
  object_id STRING,
  json_blob STRING,
);
```

Think of the content of this table as a serialized, deterministic full version of this semantic layer.

Oh! Maybe there’s also a way to compile an extended static/serialized version of this (similar to how `package.json` can generate a `package-lock.json` that can optionally be checked into the repo and materialized and diffed at each PR).

In this serialized version of the semantic layer, **everything that’s being inferred is SPELLED OUT**, meaning you’ll be able to actually see how tables will be joined, what metrics are inferred, …

### Implementation

Proposed implementation is in python as a dbapi driver + sqlalchemy dialect.

- in-memory cache of the whole semantic layer seems important, maybe it can boostrap
- ability to transpile from simple ANSI SQL to any dialect (using something like `sqlglot` library

# So what’s in the repo?

How are things semantically defined?

## “targets” (aka environment) semantics

dbt has this notion of targets (environments) and it’s pretty vital. A place where you can define dev/staging/prod and what they point to. For dbt it’s in `.dbt/profiles.yaml` but you can override and such. We need that. Maybe our targets are dbt-compatible? 🙂 dbt inspired?

a set of yaml files? templated? 

```bash
	repo/
  project.yaml # similar to dbt_project, high level configs

  # enriching semantics
  joins.yaml
  metrics.yaml
  dimensions.yaml
  contexts.yaml
  ...

  ## alternatively or complementarilly objects can be defined as code
  joins.py
  metrics.py
  ...

  ## this is dynamically generated by the CLI, can be checked in or not
  compiled/ 
    ## storing the physical representation of all the tables in the input schema
    physical/
      dim_customers.yaml
      dim_time.yaml
      fact_sales.yaml
    ## semantics, mixing the inferred + enriched stuff
    joins.yaml
    metrics.yaml
    dimensions.yaml
    contexts.yaml
   
```

Read the content of **/*.yaml and merge all that into a big semantic layer object?

## A CLI

Writing down some useful things

```bash

# read the physical schema, make inferences, merge the enrichemnts
# generate the compiled/ folder
$ semantic_layer_tool compile env=dev

# push the semantic layer a given database
$ semantic_layer_tool push env=dev
```
