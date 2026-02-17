# Upstash Redis Setup for Helios-Chad Communication

## Free Tier Limits
- 256MB data size
- 500,000 commands/month (~16,000/day)
- 10GB bandwidth/month
- 1 database per account

## Setup Instructions

### 1. Create Upstash Account
1. Go to https://upstash.com
2. Sign up with GitHub or email
3. Create new Redis database
4. Choose region closest to you (Singapore for Asia)

### 2. Get Connection Details
After creating database, you'll get:
```
REDIS_URL=redis://default:PASSWORD@HOST:PORT
```

### 3. Configure Environment
Add to `.env` or export:
```bash
export UPSTASH_REDIS_URL="redis://default:xxxxx@xxxxx.upstash.io:6379"
```

### 4. Test Connection
```python
import redis
import os

r = redis.from_url(os.environ['UPSTASH_REDIS_URL'])
r.ping()  # Should return True
r.set('test', 'hello')
print(r.get('test'))  # b'hello'
```

## Architecture

```
┌─────────┐      Redis Pub/Sub      ┌─────────┐
│ Helios  │ ◄──────────────────────► │  Chad   │
│ (Cloud) │   channels:              │ (Local) │
│         │   - helios→chad          │         │
│         │   - chad→helios          │         │
│         │   - broadcast            │         │
└─────────┘                          └─────────┘
```

## Usage Example

### Helios side:
```python
import redis
import os

r = redis.from_url(os.environ['UPSTASH_REDIS_URL'])
pubsub = r.pubsub()
pubsub.subscribe('chad→helios')

# Send message to Chad
r.publish('helios→chad', json.dumps({
    'from': 'helios',
    'type': 'task',
    'data': {...}
}))

# Receive from Chad
for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        print(f"From Chad: {data}")
```

### Chad side:
```python
import redis
import os

r = redis.from_url(os.environ['UPSTASH_REDIS_URL'])
pubsub = r.pubsub()
pubsub.subscribe('helios→chad')

# Send message to Helios
r.publish('chad→helios', json.dumps({
    'from': 'chad',
    'type': 'response',
    'data': {...}
}))

# Receive from Helios
for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        print(f"From Helios: {data}")
```

## Channels

| Channel | Direction | Purpose |
|---------|-----------|---------|
| `helios→chad` | Helios → Chad | Commands, tasks |
| `chad→helios` | Chad → Helios | Responses, status |
| `broadcast` | Both ways | Announcements |
| `agent.{name}` | Specific | Agent-specific |
| `heartbeat` | Both ways | Health checks |

## Cost Estimation

For 20 agents, 1000 messages/day:
- 20 agents × 1000 msgs × 30 days = 600,000 commands/month
- **Within free tier** (500K limit, slight overage acceptable)

If exceeded: $0.20 per 100K commands = ~$0.40/month

## Fallback

If Redis fails, fall back to GitHub:
```python
try:
    r.ping()
    use_redis()
except:
    use_github_fallback()
```

## Security

- Use TLS (rediss://) for encrypted connection
- Store credentials in environment variables
- Rotate keys monthly

## Next Steps

1. Create Upstash account
2. Get REDIS_URL
3. Test connection
4. Deploy to both Helios and Chad
5. Verify real-time messaging
