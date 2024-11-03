# Solr 101: Basic Search Commands

These examples cover the most common basic search operations in Solr. Remember to:
- Always test queries with a small subset first
- Use appropriate field names for your schema
- Check the response format matches your needs
- Consider performance implications for large result sets

## Basic Query Structure
```bash
http://localhost:8983/solr/[collection-name]/select?[parameters]
```

## Simple Searches

### 1. Match All Documents
```bash
q=*:*
```

### 2. Single Term Search
```bash
# Search for 'phone' in all fields
q=phone

# Search in specific field
q=name:phone
```

### 3. Exact Phrase Searches
```bash
# Search for exact phrase
q="samsung galaxy"

# In specific field
q=product_name:"samsung galaxy"
```

### 4. Field-Specific Searches
```bash
# Price equals 100
q=price:100

# Product name contains 'laptop'
q=name:laptop

# Category is 'electronics'
q=category:electronics
```

### 5. Boolean Operators
```bash
# AND operator
q=name:samsung AND price:500

# OR operator
q=category:phones OR category:tablets

# NOT operator
q=category:electronics NOT brand:apple
```

### 6. Range Queries
```bash
# Price between 100 and 500
q=price:[100 TO 500]

# Price greater than 100
q=price:[100 TO *]

# Price less than 500
q=price:[* TO 500]

# Date range
q=date:[2023-01-01T00:00:00Z TO 2023-12-31T23:59:59Z]
```

### 7. Pagination
```bash
# First 10 results
q=*:*&rows=10&start=0

# Next 10 results
q=*:*&rows=10&start=10
```

### 8. Sorting
```bash
# Sort by price ascending
q=*:*&sort=price asc

# Sort by price descending
q=*:*&sort=price desc

# Sort by multiple fields
q=*:*&sort=price asc,name asc
```

### 9. Field Selection
```bash
# Return only specific fields
q=*:*&fl=name,price,category

# Return all fields
q=*:*&fl=*
```

### 10. Simple Faceting
```bash
# Facet by category
q=*:*&facet=true&facet.field=category

# Facet by price ranges
q=*:*&facet=true&facet.range=price&facet.range.start=0&facet.range.end=1000&facet.range.gap=100
```

### 11. Wildcard Searches
```bash
# Starts with 'sam'
q=name:sam*

# Ends with 'phone'
q=name:*phone

# Contains 'pro'
q=name:*pro*
```

### 12. Basic Filter Queries
```bash
# Filter by category
q=*:*&fq=category:electronics

# Filter by price
q=*:*&fq=price:[0 TO 100]
```

### 13. Simple Text Matching
```bash
# Case-insensitive search
q=name:PHONE

# Multiple terms
q=name:(phone charger)
```

### 14. Existence Queries
```bash
# Field exists
q=description:[* TO *]

# Field does not exist
q=-description:[* TO *]
```

### 15. Boolean Field Queries
```bash
# Items in stock
q=inStock:true

# Items not in stock
q=inStock:false
```

### 16. Basic Grouping
```bash
# Group by category
q=*:*&group=true&group.field=category

# Group with limit
q=*:*&group=true&group.field=category&group.limit=3
```

### 17. Simple Stats
```bash
# Get stats on price
q=*:*&stats=true&stats.field=price

# Get stats on multiple fields
q=*:*&stats=true&stats.field=price&stats.field=rating
```

### 18. Basic Highlighting
```bash
# Highlight matched terms
q=name:phone&hl=true&hl.fl=name

# Highlight with custom tags
q=name:phone&hl=true&hl.fl=name&hl.simple.pre=<em>&hl.simple.post=</em>
```

### 19. Simple Spell Checking
```bash
# Get spelling suggestions
q=name:phne&spellcheck=true

# Get extended suggestions
q=name:phne&spellcheck=true&spellcheck.collate=true
```

### 20. Response Formatting
```bash
# Get response in JSON format
q=*:*&wt=json

# Get response in XML format
q=*:*&wt=xml
```

## Common Use Cases

### Product Search
```bash
# Basic product search
q=name:laptop&fq=category:electronics&fq=inStock:true

# Product search with price filter
q=name:laptop&fq=price:[500 TO 1000]&fq=inStock:true&sort=price asc
```

### Category Browse
```bash
# List all items in category
q=category:electronics&sort=name asc

# List items in category with price range
q=category:electronics&fq=price:[0 TO 500]&sort=price asc
```

### Search with Metadata
```bash
# Search with brand and model
q=brand:samsung AND model:galaxy

# Search with specifications
q=name:phone AND features:5G
```

### Date-Based Queries
```bash
# Items added today
q=dateAdded:[NOW-1DAY TO NOW]

# Items from last week
q=dateAdded:[NOW-7DAYS TO NOW]
```

### Stock Status
```bash
# In-stock items on sale
q=inStock:true AND onSale:true

# Low stock items
q=stockCount:[0 TO 10]
```

## Tips for Basic Searches

1. **Field Names**
```bash
# Always check field names are correct
q=product_name:phone    # if field is named 'product_name'
q=name:phone           # if field is named 'name'
```

2. **Special Characters**
```bash
# Escape special characters
q=name:iPhone\+
q=model:Samsung\-A52
```

3. **Multiple Values**
```bash
# Multiple values for same field
q=category:(electronics computers)
```

4. **Combining Searches**
```bash
# Combine multiple conditions
q=category:electronics AND price:[100 TO 500] AND inStock:true
```

5. **Common Parameters**
```bash
# Limit results
rows=10

# Start position
start=0

# Sort order
sort=price desc

# Field list
fl=name,price,description
```

