# Vector Search in Solr Exercise

## Initial Setup

### Collection Creation
*Create* a new collection:
```bash
bin/solr create -c films
```

### Schema Configuration
*Update* schema with vector configurations:

| Field | Type | Properties |
|-------|------|------------|
| **film_vector** | knn_vector_10 | dimension: 10, similarity: cosine |
| **name** | text_general | stored, single-valued |
| **initial_release_date** | pdate | stored |

```json
curl http://localhost:8983/solr/films/schema -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field-type" : {
    "name":"knn_vector_10",
    "class":"solr.DenseVectorField",
    "vectorDimension":10,
    "similarityFunction":"cosine",
    "knnAlgorithm":"hnsw"
  },
  "add-field" : [
      {
        "name":"film_vector",
        "type":"knn_vector_10",
        "indexed":true,
        "stored":true
      },
      {
        "name":"name",
        "type":"text_general",
        "multiValued":false,
        "stored":true
      },
      {
        "name":"initial_release_date",
        "type":"pdate",
        "stored":true
      }
    ]
}'
```

### Data Indexing
*Index* the data:
```bash
bin/solr post -c films example/films/films.json
```

## Vector Search Examples

### Target Vector
Based on: **Finding Nemo**, **Bee Movie**, **Harry Potter**
```
[-0.1784, 0.0096, -0.1455, 0.4167, -0.1148, -0.0053, -0.0651, -0.0415, 0.0859, -0.1789]
```

### Search Operations

| Operation | Description | Query Type |
|-----------|-------------|------------|
| *Find* similar movies | Top 10 similar to target | KNN Query |
| *Filter* watched movies | Exclude specific IDs | KNN + Filter |
| *Search* specific movies | Name contains "cinderella" | KNN as Filter |
| *Rerank* results | Combine scores | KNN with ReRanking |
| *Custom ranking* | Vector similarity + text relevance | Combined Scoring |

### Advanced Query Examples

#### Simple KNN
```
http://localhost:8983/solr/films/query?q={!knn f=film_vector topK=10}[-0.1784,...]
```

#### KNN with Filtering
```
http://localhost:8983/solr/films/query?q={!knn f=film_vector topK=10}[-0.1784,...]&fq=-id:("...")
```

#### Combined Scoring
```
http://localhost:8983/solr/films/query?q=name:batman&q_lexical={!edismax v=$q}&q_vector={!knn f=film_vector topK=10000}[-0.1784,...]&score_combined=sum(mul(scale($q_lexical,0,1),0.7),mul(scale($q_vector,0,1),0.3))
```

## Key Takeaways

- Vector fields enable **similarity-based** search
- Combines traditional text search with *vector operations*
- Supports **filtering**, *reranking*, and score combinations
- Useful for recommendation systems and content similarity