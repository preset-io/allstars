class Join(MenuItem):
    left_relation_key: str
    right_relation_key: str
    join_criteria: str
    cardinality: Literal["many_to_one", "one_to_many", "many_to_many"]
    join_term: Literal["JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"]
