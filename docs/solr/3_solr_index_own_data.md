# Solr Data Indexing Exercise Guide

## Core Concepts
| Aspect | Details |
|--------|----------|
| Main Focus | **Data indexing** in Solr with custom datasets |
| Collection Setup | *Create new collection* with configset |
| Schema Note | Uses **_default configset** with schemaless features |

## Collection Creation
```bash
bin/solr create -c localDocs -s 2 -rf 2
```

## Indexing Methods
| Method | Description |
|--------|-------------|
| **Post Tool** | *Index local files* (JSON, XML, CSV, HTML, PDF, MS Office) |
| **SolrJ** | Java-based client for programmatic indexing |
| **Admin UI** | Web interface for manual document indexing |

### Example Post Tool Usage
```bash
bin/solr post -c localDocs ~/Documents
```

## Data Management
| Operation | Command Example |
|-----------|----------------|
| *Update* | Auto-replaces documents with same **uniqueKey** |
| *Delete Single* | `bin/solr post -c localDocs -d "<delete><id>SP2514N</id></delete>"` |
| *Delete All* | `bin/solr post -c localDocs -d "<delete><query>*:*</query></delete>"` |

## Key Metrics
| Metric | Description |
|--------|-------------|
| **numDocs** | Count of searchable documents |
| **maxDoc** | Total documents including deleted ones |

## Planning Considerations
- Data types for indexing
- Field configuration
- Analysis rules
- Search functionality
- Testing requirements