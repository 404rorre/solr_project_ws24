# Exercise 4: Using ParamSets Guide

## Initial Setup

### Collection Creation
*Create new films collection*:
```bash
bin/solr create -c films
```

### Schema Configuration
*Update schema via POST request*:
```bash
curl http://localhost:8983/solr/films/schema -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field" : [
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

Key field configurations:
| Field | Type | MultiValued | Stored |
|-------|------|-------------|--------|
| **name** | text_general | false | true |
| **initial_release_date** | pdate | false | true |

## Data Operations

### Indexing
*Index sample data*:
```bash
bin/solr post -c films example/films/films.json
```

## Search Examples

### Basic Searches
1. *Search for Batman*:
```
http://localhost:8983/solr/films/query?q=name:batman
```

2. *Filter superhero movies*:
```bash
curl 'http://localhost:8983/solr/films/query?q=*:*&fq=genre:"Superhero movie"'
```

3. *Genre distribution*:
```bash
curl 'http://localhost:8983/solr/films/query?q=*:*&facet=true&facet.field=genre'
```

## ParamSet Implementation

### Configuration
*Create algorithm configurations*:
```bash
curl http://localhost:8983/solr/films/config/params -X POST -H 'Content-type:application/json' --data-binary '{
"set": {
    "algo_a":{
      "defType":"dismax",
      "qf":"name"
    }
  },
  "set": {
    "algo_b":{
      "defType":"dismax",
      "qf":"name",
      "mm":"100%"
    }
  }
}'
```

Algorithm comparison:
| Parameter | Algo A | Algo B |
|-----------|--------|--------|
| **defType** | dismax | dismax |
| **qf** | name | name |
| **mm** | - | 100% |

### Testing
1. *Algorithm A query*:
```
http://localhost:8983/solr/films/query?q=harry%20potter&useParams=algo_a
```

2. *Algorithm B query*:
```
http://localhost:8983/solr/films/query?q=harry%20potter&useParams=algo_b
```

## Results Analysis
- **Algorithm A**: Returns 5 results including non-relevant matches
- **Algorithm B**: Returns 4 results with *improved precision* focusing on Harry Potter films only