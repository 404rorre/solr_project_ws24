# Solr Schema Key-Value Pairs Reference

## Basic Field Properties

| Property | Possible Values | Default | Description |
|----------|----------------|---------|-------------|
| name | Any string | Required | Field identifier |
| type | text_general, string, pint, pfloat, plong, pdouble, date, boolean, binary, point, location, uuid, text_ws, text_general_rev, text_en, text_en_splitting, text_en_splitting_tight | Required | Data type of the field |
| stored | true/false | true | Whether original value is stored |
| indexed | true/false | true | Whether field is searchable |
| multiValued | true/false | false | Can contain multiple values |
| required | true/false | false | Field is mandatory |
| docValues | true/false | false | Enable sorting/faceting |

## Advanced Field Properties

| Property | Possible Values | Default | Description |
|----------|----------------|---------|-------------|
| omitNorms | true/false | false | Disable norms calculation |
| omitTermFreqAndPositions | true/false | false | Disable term freq/position |
| omitPositions | true/false | false | Disable position storage |
| termVectors | true/false | false | Store term vectors |
| termPositions | true/false | false | Store positions in term vectors |
| termOffsets | true/false | false | Store offsets in term vectors |
| termPayloads | true/false | false | Store payloads in term vectors |
| large | true/false | false | Field may contain large values |

## Text Analysis Properties

| Property | Possible Values | Default | Description |
|----------|----------------|---------|-------------|
| positionIncrementGap | Integer (usually 100) | 0 | Position gap between values |
| analyzer/tokenizer class | solr.StandardTokenizerFactory, solr.WhitespaceTokenizerFactory, solr.KeywordTokenizerFactory, solr.LetterTokenizerFactory, solr.NGramTokenizerFactory, solr.EdgeNGramTokenizerFactory, solr.ICUTokenizerFactory | None | Tokenizer for text analysis |

## Common Filter Factories

| Filter Factory | Parameters | Description |
|----------------|------------|-------------|
| LowerCaseFilterFactory | None | Convert to lowercase |
| StopFilterFactory | words="stopwords.txt", ignoreCase=true | Remove stop words |
| SynonymGraphFilterFactory | synonyms="synonyms.txt", expand=true, ignoreCase=true | Handle synonyms |
| WordDelimiterGraphFilterFactory | generateWordParts=1, generateNumberParts=1, catenateWords=0, catenateNumbers=0, catenateAll=0, splitOnCaseChange=1 | Complex word splitting |
| ICUFoldingFilterFactory | None | Unicode text folding |
| SnowballPorterFilterFactory | language="English" | Stemming |

## Dynamic Field Patterns

| Pattern | Example | Description |
|---------|---------|-------------|
| *_txt, *_s, *_i, *_l, *_t, *_b, *_dt, *_p | field_txt, field_s, field_i, etc. | Common dynamic field patterns |

## Common Field Types and Their Classes

| Field Type | Class | Description |
|------------|-------|-------------|
| string | solr.StrField | String values |
| pint | solr.IntPointField | Integer values |
| pfloat | solr.FloatPointField | Float values |
| plong | solr.LongPointField | Long values |
| pdouble | solr.DoublePointField | Double values |
| date | solr.DatePointField | Date values |
| boolean | solr.BoolField | Boolean values |
| binary | solr.BinaryField | Binary data |
| point | solr.PointField | Multi-dimensional points |
| location | solr.LatLonPointSpatialField | Geographical coordinates |
| uuid | solr.UUIDField | Universally unique identifiers |

## Currency Field Properties

| Property | Possible Values | Default | Description |
|----------|----------------|---------|-------------|
| defaultCurrency | ISO 4217 codes (USD, EUR, etc.) | USD | Default currency |
| precisionStep | Integer | 8 | Precision for range queries |
| amountLongSuffix | String | "l_raw" | Suffix for the amount |
| codeStrSuffix | String | "_currency" | Suffix for currency code |

## Date Field Properties

| Property | Possible Values | Default | Description |
|----------|----------------|---------|-------------|
| formatDate | NOW, DATE, DAY, HOUR, MINUTE, SECOND, YEAR, MONTH | None | Date format pattern |
| autoCreateFields | true/false | true | Auto-create date fields |

## Spatial Field Properties

| Property | Possible Values | Default | Description |
|----------|----------------|---------|-------------|
| spatialContextFactory | JTS, Legacy | JTS | Spatial context implementation |
| units | degrees, kilometers, miles | degrees | Distance units |
| distanceUnits | degrees, kilometers, miles | kilometers | Distance measure units |
| geodetic | true/false | true | Use geodetic calculations |