# Solr Advanced: Complex Search Commands

Remember:
- These advanced queries can significantly impact performance
- Test thoroughly with representative data volumes
- Monitor memory usage and cache efficiency
- Consider impact on other concurrent users
- Use explain to understand scoring
- Profile queries before production use

## Advanced Query Syntax

### 1. Complex Boolean Queries
```bash
# Nested boolean expressions
q=((category:electronics AND brand:samsung) OR (category:phones AND price:[500 TO 1000])) AND inStock:true

# Boolean operators with boost
q=title:(smartphone^2 OR "mobile phone"^1.5) AND manufacturer:samsung
```

### 2. Advanced Field Queries
```bash
# Multiple fields with different boosts
q=name:phone^2 OR description:phone^0.5

# Complex field grouping
q=+name:(+samsung +galaxy) +(category:phone category:tablet)
```

### 3. Function Queries
```bash
# Using mathematical functions
q={!func}sum(price,mul(quantity,2))

# Complex scoring function
q={!func}div(pow(price,2),sum(rank,1))
```

### 4. Distance Queries
```bash
# Geospatial search within radius
q=*:*&fq={!geofilt sfield=location pt=40.7128,-74.0060 d=5}

# Geospatial with boost by distance
q={!boost f=recip(geodist(),2,200,20)}
```

### 5. Advanced Faceting
```bash
# Pivot faceting
facet=true&facet.pivot=category,brand,price

# Range faceting with multiple ranges
facet=true&facet.range=price&facet.range.start=0&facet.range.end=1000&facet.range.gap=50&facet.range=rating&facet.range.start=1&facet.range.end=5&facet.range.gap=0.5
```

### 6. Complex Json Faceting
```bash
json.facet={
  categories:{
    type:terms,
    field:category,
    facet:{
      avg_price:"avg(price)",
      ranges:{
        type:range,
        field:price,
        start:0,
        end:1000,
        gap:100
      }
    }
  }
}
```

### 7. Advanced Grouping
```bash
# Group with sorting and formatting
group=true&group.field=category&group.sort=price desc&group.format=simple&group.main=true

# Group with function query
group=true&group.func=div(price,50)&group.ngroups=true
```

### 8. Complex Joins
```bash
# Parent-child join
q={!parent which="type:parent"}child_field:value

# Cross-collection join
q={!join from=id to=parent_id fromIndex=children}category:toys
```

### 9. Custom Scoring
```bash
# Boost by function
q=name:phone&bf=recip(rord(price),1,1000,1000)

# Multiple boost functions
q=name:phone&bf=price^0.5&bf=rating^2
```

### 10. Advanced Highlighting
```bash
# Custom fragmenter with weights
hl=true&hl.fl=description&hl.fragmenter=regex&hl.fragsize=100&hl.regex.slop=0.6&hl.regex.pattern=\w+(&\w+)*

# Highlight with FastVector
hl=true&hl.method=fastVector&hl.fl=description&hl.snippets=3
```

### 11. Complex Stats
```bash
# Stats with faceting
stats=true&stats.field={!tag=prc}price&facet=true&facet.field={!ex=prc}category

# Stats with multiple functions
stats=true&stats.field={!func}sum(price,tax)&stats.facet=category
```

### 12. Advanced Spell Checking
```bash
# Contextual spellcheck
spellcheck=true&spellcheck.dictionary=context&spellcheck.accuracy=0.7&spellcheck.collate=true

# Multiple dictionary spellcheck
spellcheck=true&spellcheck.dictionary=default&spellcheck.dictionary=wordbreak
```

### 13. MLT (More Like This)
```bash
# MLT with custom parameters
mlt=true&mlt.fl=name,description&mlt.mindf=1&mlt.mintf=1&mlt.boost=true

# MLT with query filtering
mlt=true&mlt.fl=name,description&mlt.qf=name^10.0 description^0.5
```

### 14. Complex Filter Queries
```bash
# Multiple nested filters
fq={!tag=cat}category:electronics&fq={!tag=prc}price:[100 TO 500]&facet.field={!ex=cat}category

# Filter with function query
fq={!frange l=0 u=100}mul(popularity,price)
```

### 15. Advanced Sorting
```bash
# Sort by function
sort=sum(popularity,product(price,0.1)) desc

# Sort by distance
sort=geodist(45.15,-93.85) asc
```

### 16. Complex Time Queries
```bash
# Date math with custom format
q=timestamp:[NOW-7DAYS/DAY TO NOW/DAY+1DAY]

# Date faceting with custom intervals
facet.date=timestamp&facet.date.start=NOW/HOUR-24HOURS&facet.date.end=NOW/HOUR&facet.date.gap=+1HOUR
```

### 17. Expert Level Relevancy Tuning
```bash
# Custom similarity with boosts
defType=edismax&q=name:phone description:smartphone&qf=name^10 description^4&pf=name^50&ps=2

# Field length normalization
q={!lucene}+name:phone +_val_:"norm(price)"
```

### 18. Advanced Grouping with Collapsing
```bash
# Field collapsing with top N per group
fq={!collapse field=category max=sum(price,product(popularity,2))}

# Collapse with expand
fq={!collapse field=category}&expand=true&expand.rows=5
```

### 19. Complex JSON Request Handler
```bash
{
  "query": "name:phone",
  "filter": ["price:[100 TO 500]", "inStock:true"],
  "boost": {
    "multiply": [
      { "field": "popularity" },
      { "func": "recip(ms(NOW,timestamp),3.16e-11,1,1)" }
    ]
  }
}
```

### 20. Advanced Analytics
```bash
# Percentile calculations
stats=true&stats.field={!percentiles="1,5,25,50,75,95,99"}price

# Cardinality and count distinct
stats=true&stats.field={!cardinality=true}category
```

## Expert Tips

1. **Performance Optimization**
```bash
# Cache warming
qt=/admin/file&action=ENABLEPREFETCH&name=warming

# Field loading optimization
fl=id,[docid],[explain],score
```

2. **Debug Options**
```bash
# Debug query
debug=true&debug.explain.structured=true

# Timing breakdown
debug.timing=true&debug.query=true
```

3. **Custom Scoring**
```bash
# Complex function queries
bf=recip(rord(mybool),1,1000,1000)
bf=product(popularity,recip(rord(price),1,1000,1000))
```

4. **Advanced Caching**
```bash
# Cache control
cache=false&logParamsList=cache&debugQuery=true

# Cache warming queries
fq={!cache=false}category:electronics
```

5. **Expert Parameters**
```bash
# Term vector analysis
tv=true&tv.tf=true&tv.df=true&tv.positions=true

# Custom similarity
similarity=BM25Similarity
```

