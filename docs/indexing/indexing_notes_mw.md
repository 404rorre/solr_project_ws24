# Indexing
More a trial and error and playing around to show something.

## Indexing fields
| Field Name | Used | Comment | Solr Field Type | Common Properties |
|------------|------|---------|-----------------|-------------------|
| cord_uid   | □ | | | |
| sha        | □ | | | |
| source_x   | ✓ | | | |
| title      | ✓ | | | |
| doi        | ✓ | | | |
| pmcid      | □ | | | |
| pubmed_id  | ✓ | | | |
| license    | □ | | | |
| abstract   | ✓ | | | |
| publish_time | □ | | | |
| authors    | ✓ | | | |
| journal    | □ | | | |
| mag_id     | □ | | | |
| who_covidence_id | □ | | | |
| arxiv_id   | □ | | | |
| pdf_json_files | □ | | | |
| pmc        | □ | | | |

Usage Guide:
- Used: Check (✓) if you're using this field
- Comment: Add any notes about how you're using the field
- Solr Field Type: Fill in the Solr field type you're using
- Common Properties: List the properties you've applied

## Converting Fields
### publish_time
publish_time has some `nan` and some `YYYY` dates, where as all other dates are in the `YYYY-MM-DD` format.
Using `data_manipulation/index_fix_publish_time.py`:
* `nan` -> `0000-00-00`
* `YYYY` -> `YYYY-00-00`

### authors
Playing around with the separator. Changed it to `|` but `;` should be fine as well.
**Important!**
Use `multiValued` feature in solr, as this field contains more then one entry. 

## Adding Features
### Catchall copy field
```bash
curl -X POST -H 'Content-type:application/json' --data-binary '{"add-copy-field" : {"source":"*","dest":"_text_"}}' http://localhost:8983/solr/covid/schema
```

## Indexing command
```bash
./solr post -c covid data/index/metadata.csv --params "f.authors.split=true&f.authors.separator=|&skip=arxiv_id&header=true"
```