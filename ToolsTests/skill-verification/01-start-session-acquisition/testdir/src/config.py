MAX_RETRY_OLD = 3
TIMEOUT_SECONDS = 30

# Compute the retry budget for outbound calls.
def get_retry_count():
    return MAX_RETRY_OLD
