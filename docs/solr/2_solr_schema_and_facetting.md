# Solr Films Data Indexing Exercise Summary

## Setup and Collection Creation
- *Restart Solr* if needed:
```bash
bin/solr start -c -p 8983 -s example/cloud/node1/solr
bin/solr start -c -p 7574 -s example/cloud/node2/solr -z localhost:9983
```
- *Create new collection* named "films":
```bash
bin/solr create -c films -s 2 -rf 2
```

## Schema Configuration
| Component | Purpose | Implementation |
|-----------|---------|----------------|
| **Managed Schema** | Only modified via Schema API | No manual edits |
| **Field Guessing** | Auto-creates fields during indexing | Not recommended for production |

### Required Schema Changes
1. *Create "names" field*:
```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{"add-field": {"name":"name", "type":"text_general", "multiValued":false, "stored":true}}' http://localhost:8983/solr/films/schema
```

2. *Create catchall copy field*:
```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{"add-copy-field" : {"source":"*","dest":"_text_"}}' http://localhost:8983/solr/films/schema
```

## Indexing Data
*Choose one format to index*:
```bash
# JSON
bin/solr post -c films example/films/films.json

# XML
bin/solr post -c films example/films/films.xml

# CSV
bin/solr post -c films example/films/films.csv --params "f.genre.split=true&f.directed_by.split=true&f.genre.separator=|&f.directed_by.separator=|"
```

## Faceting Features

### Field Faceting
- *Basic facet query*:
```bash
curl "http://localhost:8983/solr/films/select?q=*:*&rows=0&facet=true&facet.field=genre_str"
```

### Range Faceting
- *Date range example*:
```bash
curl "http://localhost:8983/solr/films/select?q=*:*&rows=0\
&facet=true\
&facet.range=initial_release_date\
&facet.range.start=NOW/YEAR-25YEAR\
&facet.range.end=NOW\
&facet.range.gap=%2B1YEAR"
```

### Pivot Faceting
- *Nested faceting example*:
```bash
curl "http://localhost:8983/solr/films/select?q=*:*&rows=0&facet=on&facet.pivot=genre_str,directed_by_str"
```

## Cleanup
*Delete collection*:
```bash
bin/solr delete -c films
```