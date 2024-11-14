# Curl Command Options Reference

## Basic Request Options

| Option | Short | Long Form | Description | Example |
|--------|--------|-----------|-------------|----------|
| `-X` | `-X` | `--request` | Specify HTTP method | `curl -X POST url` |
| `-H` | `-H` | `--header` | Set HTTP header | `curl -H "Content-Type: application/json" url` |
| `-d` | `-d` | `--data` | Send POST data | `curl -d "name=value" url` |
| `-G` | `-G` | `--get` | Send GET request | `curl -G url` |
| `-I` | `-I` | `--head` | Show document info only | `curl -I url` |

## Data Transfer Options

| Option | Short | Long Form | Description | Example |
|--------|--------|-----------|-------------|----------|
| `-F` | `-F` | `--form` | Upload form data | `curl -F "file=@photo.jpg" url` |
| `--data-binary` | N/A | `--data-binary` | Post data exactly as specified | `curl --data-binary @file.json url` |
| `--data-raw` | N/A | `--data-raw` | Post data without processing | `curl --data-raw "raw data" url` |
| `--data-urlencode` | N/A | `--data-urlencode` | URL encode data | `curl --data-urlencode "name=John Doe" url` |

## Authentication Options

| Option | Short | Long Form | Description | Example |
|--------|--------|-----------|-------------|----------|
| `-u` | `-u` | `--user` | User authentication | `curl -u username:password url` |
| `-E` | `-E` | `--cert` | Client certificate | `curl -E cert.pem url` |
| `--basic` | N/A | `--basic` | Use basic auth | `curl --basic -u user:pass url` |
| `--digest` | N/A | `--digest` | Use digest auth | `curl --digest -u user:pass url` |

## Output Options

| Option | Short | Long Form | Description | Example |
|--------|--------|-----------|-------------|----------|
| `-o` | `-o` | `--output` | Write to file | `curl -o file.html url` |
| `-O` | `-O` | `--remote-name` | Save with remote name | `curl -O url/file.zip` |
| `-s` | `-s` | `--silent` | Silent mode | `curl -s url` |
| `-v` | `-v` | `--verbose` | Verbose output | `curl -v url` |
| `-w` | `-w` | `--write-out` | Format output | `curl -w "%{http_code}" url` |

## Connection Options

| Option | Short | Long Form | Description | Example |
|--------|--------|-----------|-------------|----------|
| `-k` | `-k` | `--insecure` | Allow insecure connections | `curl -k https://url` |
| `-L` | `-L` | `--location` | Follow redirects | `curl -L url` |
| `--max-time` | `-m` | `--max-time` | Maximum time allowed | `curl --max-time 10 url` |
| `--connect-timeout` | N/A | `--connect-timeout` | Connection timeout | `curl --connect-timeout 5 url` |
| `-x` | `-x` | `--proxy` | Use proxy | `curl -x proxy:port url` |

## Cookie Options

| Option | Short | Long Form | Description | Example |
|--------|--------|-----------|-------------|----------|
| `-b` | `-b` | `--cookie` | Send cookies | `curl -b "session=123" url` |
| `-c` | `-c` | `--cookie-jar` | Save cookies | `curl -c cookies.txt url` |
| `--cookie-jar` | N/A | `--cookie-jar` | Save cookies to file | `curl --cookie-jar file.txt url` |

## Common Combinations

```bash
# POST JSON data with auth
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer token123" \
     --data-binary @data.json \
     https://api.example.com/endpoint

# Download with progress and follow redirects
curl -O -L -# https://example.com/file.zip

# Form submission with file upload
curl -X POST \
     -F "file=@document.pdf" \
     -F "description=My File" \
     https://upload.example.com

# Verbose debugging with certificate
curl -v \
     -E cert.pem \
     -H "Authorization: Bearer token123" \
     https://secure.example.com
```

## Pro Tips

1. Use `\` for line breaks in complex commands
2. Use `@filename` to read data from files
3. Add `-v` for debugging
4. Use `-s` with jq for JSON processing: `curl -s url | jq .`
5. Save common options in `~/.curlrc`