from datetime import datetime

FULL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MINUTE_FORMAT = "%Y-%m-%d %H:%M"
DATE_FORMAT = "%Y-%m-%d"
ADD_CHUNK_CODE_OP = "POST"
GET_BLOCK_BY_HASH_OP = "GETH"
GET_BLOCKS_BY_TIMESTAMP_OP = "GETT"
GET_STATS_OP = "STAT"
OPERATION_TIMEOUT = 5

def get_and_format_datetime_now():
    return datetime.now().strftime(FULL_DATE_FORMAT)

def number_to_4_bytes(num):
    result = bytearray()
    for i in range(4):
        result.append(num & 255)
        num = num >> 8
    return result

def bytes_4_to_number(b):
    res = 0
    for i in range(4):
        res += b[i] << (i*8)
    return res

def empty_queue(queue):
    while not queue.empty():
        queue.get()