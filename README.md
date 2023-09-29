# SQL All ⭐ Stars 

<img width=600 src="https://github.com/preset-io/estrella/assets/487433/390e73c4-f99b-4912-a6b2-830b0b9a0375">


## A Smart & Progressive Semantic Layer

SQL All ⭐ Stars or `allstars` is a smart semantic layer that takes
a new approach:

- **mostly inferred:** it looks at your physical schema and makes
  educated guesses around your semantics (joins, metrics, dimensions,
  hierarchies). Eventually it will also look at your usage patterns
  to infer more useful semantics.
- **progressively enrichable:** building on it's inferences, you can
  curate, enrich and rewire things as needed at your own pace. It's useful
  on day 0, and becomes more useful as you extend the semantics.
- **served as a virtual database:** it exposes itself primarily
  as a simple database, as one or many collections of flat tables. This
  means it's universally adopted by anything that can talk to a database.
  Under the hood, allstars takes your simple SQL against those wide tables,
  and transpiles the SQL into more complex SQL doing the joining, the
  union-ing and whatever else is needed to get to your data
- **RESTful too:** get all the JSONs you need here too, allowing deeper
  integrations beyond the virtual database
- **100% open:** unlike a lot of semantic layers that are tightly coupled
  with some BI tool, this is 100% open and self-standing

## Served as a virtual database

```sql
SELECT customer_name, SUM(units_sold), SUM(pre_orders)
FROM ⭐
GROUP BY ⭐;
```
Something that's novel about SQL All ⭐ Stars is the idea of exposing this
semantic layer primarily as a **virtual database**. This shows as a
one or many wide tables exposing essentially all of the columns that
you want to expose from your database. While you or your BI tool run
very simple SQL against large tables,
allstars transpiles this query into a more complex query against the
underlying physical schema.

Without getting too deep in the mechanics, there's one large table to rule
them all (the "superstar" ⭐ table), and one table per "query context",
representing sets of tables that can be joined together to answer queries.

```sql
SELECT ⭐ FROM ⭐.metrics;
SELECT ⭐ FROM ⭐.dimensions;
SELECT ⭐ FROM ⭐.hierachies;
SELECT ⭐ FROM ⭐.tables;
{{ #... }}
```

On top of these large tables, allstars exposes
a set of metadata tables with all the semantics
(metrics, dimensions, hierarchies, ...)

If you are curious as to how it works, the TLDR is
that it's implemented as a dbapi driver
in Python that acts as a bit of a proxy in front of your database.

## Sweet synthtactic sugar

As a "transpiler with context" allstars can allow you to sprinkle some sugar
in your SQL. Let's get ahead of ANSI SQL and implement things. Ideas
to be implemented:
- `FROM ⭐` - straight from the superstar table
- `GROUP BY ⭐` - group by all dimensions referenced in the query
- `GROUP BY ⭐.DAY` - same as above, but truncate the one time column by day,
  WEEK, MONTH or other timeframe keywords
- trailing commas aloud
- a nice hint system
- window function abstraction(?)

## RESTfull of itself

If the virtual database doesn't suit your needs, a RESTful API is also
exposed. Comprehensive calls to extract and alter semantics, transpile SQL,
sync different sources and targets, and much more.

## Compiled, serialized, versioned and broadcastable

allstars makes inferences based on your physical schema, naming
conventions and can "compiles" all this
to a static, deterministic model that can be pushed to the file system
for source control, or to a database for driver retrieval.

Some expected workflows around creating, enriching and updating your
semantics:
- **first inference:** where allstars extracts your physical models, infers
  your joins and populates dimensions and metrics
- **mechanics enrichment:** where a data engineer or analyst engineer will add new
  objects, add join criterias that could not be detected, and creates some
  rich, relevant dimensions and metrics
- **presentation erichment:** add nice labels, descriptions and slap a folder
  structure around all your metrics, dimensions and hierarchies
- **update:** your schemas have evolved, new tables and column created, time to
  `allstars extract` the latest changes in your schema to keep things up-to-date
   

As you progressively make these changes,
they are all "compiled", versioned and made static to serve
predictable outcomes.

### Sources & targets:

#### at launch
* the filesystem as a set of human readable yaml files
* API/DSL: if yaml is too verbose and you need something more dynamic,
  you can use the python objects directly, and compile to yaml
* a database, where the content is serialized into a `_meta` table

#### future
* a git repo+ref, so that the driver can load up directly from a uri
* a REST service
* s3://artifact.zip

## A Dynamic mode

In many cases you'll want the semantic layer to be deterministic and static.
This is how semantic layers typically work.

Alternatively, you can
run allstars in dynamic mode, point it to a database schema, and let it
learn the schema it's working with, and receive hints as to how to behave
as it goes. In this mode, it'll look up the physical schema, infer possible
joins, and even receive SQL-like commands to enrichment as in 

```sql
INSERT ('table1', 'table2', 'table_1.id = table2.id') INTO ⭐.joins;
INSERT ('Order Count', 'COUNT(DISTINCT order_id)', 'orders') INTO ⭐.metrics;
```

## It's driver, not a proxy!

allstars is **NOT** a service that lives somewhere in between your database
and your application, it's a Python `dbapi` driver + `sqlalchemy` dialect.
This means it's **NOT** an external service you need to launch, keep up
and observe, it's meant to be installed and used as a simple database driver
and won't delay or buffer your queries.

What if I'm not in python? well, hoping a community develops and builds
driver for other languages that interact with allstars REST service that's
written in Python.

# What's in an allstars semantic layer?

## Some internals

Opening up the hood, the semantic layer has the following internal
representation ->

### Relations

Relations, as pointers to physical **tables** and **views**, including
the underlying **columns** along with their **data types**. The semantic
layer is essentially a fancy rich map to get to these things.  SQL All ⭐ Stars
has a full in-memory representation of all this to navigate it all.

### Joins

To complete the picture from the relations, we have a full map of which
joins can be used against the underlying relations. Each join maps
two relations, has a type of join assigned (left, right, full, outer, ...)
and has its cardinality (one-to-one, one-to-many, many-to-one, ...).

### Query contexts

When semantic layers get big, it becomes large spaghetti plate of joins,
and not all joins can be followed. The general goal is to start from a
metric, and join it to it's dimension while avoiding "fan traps" where
the metric gets duplicated while following a one-to-many join.

Query contexts are effectively a collection of joins that can be used
together safely to generate a query. In traditional dimensional modeling,
where you have a collection of fact tables and dimension tables, you'll
typically have one query context per fact table. In the case of a dimensional
query where metrics from multiple fact tables are chosen along with
shared dimensions, the semantic layer will resolve by generating multiple
queries, each against a single query context, and merge the results.

## Exposed to users

The semantic layer is essentially a menu of user-relatable objects
that act as a map to more complex set and more abstract set of physical
database objects. Like on a restaurant menu, all of these objects
are clearly organized in sections and sub-sections (**folders**),
have nice **labels**, and longer **descriptions**.

### Metric

A metric is a simple aggregate SQL expression against one or many relations.
It typically will point to a single relation but can in come cases span
across relation and require a join to compute. Note that metrics
can reference other metrics, in which case they become a more complex
metric that inherits the underlying relations.

### Dimension

A dimension is a simple, non-aggregate SQL expression against one or
many relations. Like metrics, they typically a built on top of a single
relation but not always.

Note that we made the decision to use the term dimension even though
it can be confused with the idea of a dimension table in dimensional modeling
where it refers to a collection of attributes sharing the same atomicity.
Here a dimension is a dimension of the metric, and typically represents
a single "attribute", not a collection of attributes.

### Hierarchies

Hierarchies are linear collections of dimensions where we want to enable
"drilling" or "zooming" operations in the BI tool. Think of a
geospatial hierarchy may
be pointing from `Customer Zone` -> `Customer Country` -> `Customer Region`
    -> `Customer City`.

Multiple alternate hierarchies can be defined for the sames dimensions,
and while they generally should be thought of as many-to-one as you go
down the hierarchy, this is not strickly enforce in SQL All ⭐ Stars as you
may want to enable your users to drill "across" dimensions that don't have
pure many-to-one relationships.

### Folder
Folders can be used to structure how the objects defined here are organized
and presented to the user. Each folder has a key, label and description.

### Filters

Filters are simple, reusable, labeled, documented filters. This is not
commonly used and is generally reserved for filters that involve
complex logic (think subquery) and are used and reused. 



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


## Premise #2 Even more can be inferred from a query corpus

[optional but interesting, maybe a V4 kinda thing] Interestingly, if you have a corpus of SQL as say a database log of user queries or other-bi-tools generate, those in theory could be parsed to infer patterns that answers:

- which tables can be joined and how
- which metrics are commonly used (look for aggregate expressions!)
- commonly used filters

The tool could have a feature something that reads through valid SQL and suggests augmentation of the semantic layer based on query pattern. Probably AI-based.

## Premise #3 You can enrich things over time

- Business metadata is not vital, and often takes a moment to settle, let’s put in pretty label, pretty description, fancy folders structures when we get there
- Hierarchies are nice but we can do without as we start
- Things like “List of Values”, informing how a dropdown for a given dimension should be populated for instance, are nice to haves, we don’t need this on day 0
- Aggregate awareness semantics aren’t vital
- …

### Some mechanics:

- the driver has the whole semantic model in-memory
- When querying a virtual table like `FROM ⭐` , we read the SQL and transpile it into a proper SQL that can run against the physical model
- When querying metadata, serve the model straight from memory
```sql
CREATE TABLE _meta AS (
  git_sha STRING,
  object_type STRING,
  object_id STRING,
  json_blob STRING,
);
```

### Implementation

Proposed implementation is in python as a dbapi driver + sqlalchemy dialect.

- in-memory cache of the whole semantic layer seems important, maybe it can boostrap
- ability to transpile from simple ANSI SQL to any dialect (using something like `sqlglot` library

# So what’s in the repo?

See some examples here ->
https://github.com/preset-io/allstars/tree/master/examples/


## A CLI

Writing down some useful things

```bash

# read the physical schema, make inferences, merge the enrichemnts
# generate the compiled/ folder
$ semantic_layer_tool compile env=dev

# push the semantic layer a given database
$ semantic_layer_tool push env=dev
```

## Feature ideas, beyond MVP

* a way to auto-document the semantic layer, + automated ERD diagrams
* AI-powered inference tool 
* List of value caching (or redirecting) to offload the expensive SELECT DISTINCT as
  BI tools populate their filter list
