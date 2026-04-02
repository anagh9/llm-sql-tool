import redis
import os

r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv(
    'REDIS_PORT', 6379), decode_responses=True)


def get_cached_query(question):
    return r.get(f"query:{question}")


def set_cached_query(question, result):
    r.setex(f"query:{question}", int(os.getenv('CACHE_TTL')), str(result))


if __name__ == "__main__":
    # Example usage
    question = "How many users are there?"
    cached_result = get_cached_query(question)
    if cached_result:
        print(f"Cached Result: {cached_result}")
    else:
        print("No cached result found.")
