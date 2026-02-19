from redis_backbone import RedisBackbone, event_payload


class Reporter:
    def __init__(self, store: RedisBackbone, event_stream: str):
        self.store = store
        self.event_stream = event_stream

    def emit(self, event_type: str, data: dict) -> str:
        return self.store.publish_stream(self.event_stream, event_payload(event_type, data))
