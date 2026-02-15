from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
with driver.session() as s:
    r = s.run("RETURN 1 AS test")
    print(r.single()["test"])
driver.close()
