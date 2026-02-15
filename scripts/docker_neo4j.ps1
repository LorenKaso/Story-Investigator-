docker rm -f neo4j-graphrag 2>$null
docker run -d --name neo4j-graphrag -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5
