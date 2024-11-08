# Solr Quick Start Tutorial Summary

## Initial Setup

| Action | Command |
|--------|---------|
| *Start Solr* | `bin/solr start -e cloud` |
| Default Ports | Node1: **8983**, Node2: **7574** |

## Collection Creation
- *Create collection* named **techproducts**
- Configuration: *Select* **sample_techproducts_configs**
- Structure: 2 shards, 2 replicas per shard

## Data Indexing

*Index sample data* using:
```bash
bin/solr post -c techproducts example/exampledocs/*
```

## Basic Search Operations

| Search Type | Example | Description |
|------------|---------|-------------|
| Basic Search | `curl "http://localhost:8983/solr/techproducts/select?indent=on&q=*:*"` | *Returns* all documents |
| Single Term | `curl "http://localhost:8983/solr/techproducts/select?q=foundation"` | *Searches* across all fields |
| Field-Specific | `curl "http://localhost:8983/solr/techproducts/select?q=cat:electronics"` | *Limits* search to specific field |
| Phrase Search | `curl "http://localhost:8983/solr/techproducts/select?q=\"CAS+latency\""` | *Searches* exact phrase |
| Combined Search | `curl "http://localhost:8983/solr/techproducts/select?q=%2Belectronics%20%2Bmusic"` | *Uses* **+** and **-** operators |

## Cleanup Commands

```bash
# Delete collection
bin/solr delete -c techproducts

# Create new collection
bin/solr create -c <yourCollection> -s 2 -rf 2

# Stop all nodes
bin/solr stop --all
```

## Key Features
- Web interface available at `http://localhost:8983/solr/`
- **SolrCloud** mode with built-in **ZooKeeper**
- Multiple document format support (**JSON**, **XML**, **CSV**)
- Field-specific and phrase-based searching
- Flexible query syntax with combinatorial operators