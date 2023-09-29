from allstars.core.metric import Metric

metrics = [
    Metric(key="test", expression="SUM(test)", relation_keys=["core.date_spine"]),
    Metric(
        key="test",
        expression="SUM(test) / SUM(some)",
        relation_keys=["core.date_spine", "core.egaf_cohort_engagement"],
    ),
    Metric(key="test", expression="SUM(test)", relation_key="core.date_spine"),
]
print(metrics)
from allstars.core.project import Project

p = Project()
p.load()
print(p.semantic_layer.get_relation_keys_for_objects(metrics))
