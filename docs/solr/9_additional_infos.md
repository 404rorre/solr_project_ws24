# Additional Useful Solr Information

## Collection Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| Nodes | 2 | Number of Solr nodes in cluster |
| Shards | 2 | *Splits* index across nodes |
| Replicas | 2 | *Creates* backup copies per shard |

## Query Parameters

| Parameter | Example | Purpose |
|-----------|---------|---------|
| `q` | `q=*:*` | Main query parameter |
| `fl` | `fl=id` | *Limits* returned fields |
| `indent` | `indent=on` | *Formats* JSON response |
| `rows` | `rows=10` | *Controls* number of results |

## File Types Supported

| Format | Extensions | Auto-detected |
|--------|------------|---------------|
| Documents | `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx` | ✓ |
| Text | `.xml`, `.json`, `.jsonl`, `.csv` | ✓ |
| Other | `.rtf`, `.htm`, `.html`, `.txt`, `.log` | ✓ |

## Common URL Encodings

| Character | Encoded | Usage |
|-----------|---------|-------|
| Space | `+` or `%20` | *Separates* terms |
| `+` | `%2B` | *Requires* term |
| `-` | `%2D` | *Excludes* term |
| `"` | `%22` | *Encloses* phrases |

## Port Usage

| Service | Default Port | Purpose |
|---------|-------------|---------|
| Solr Node 1 | **8983** | Primary node |
| Solr Node 2 | **7574** | Secondary node |
| ZooKeeper | **9983** | Cluster coordination |
| Admin UI | **8983** | Web interface |

These tables provide quick reference for common configurations and parameters when working with Solr.