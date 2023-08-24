class QueryContext(CustomModel):
    key: str
    joins: List[JoinModel] = []
