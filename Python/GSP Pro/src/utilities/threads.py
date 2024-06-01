from psutil import virtual_memory
import threading

MEM_USED_PER_INSTANCE_IN_MB = 500.00 # Closer to 250, but better safe than sorry
MEM_USED_PER_INSTANCE_IN_BYTES = MEM_USED_PER_INSTANCE_IN_MB * (1024 * 1024) # Converts MB to Bytes for increased accuracy
AVAILABLE_SYS_MEM_IN_BYTES = virtual_memory().available

# Create a thread-local storage object
thread_local = threading.local()
thread_counter = 0

def calc_safe_threads():
    max_threads = calc_max_threads()
    if max_threads and isinstance(max_threads, float):
        return int(max_threads / 2)
    return 1

def calc_max_threads():
    try:
        max_threads = AVAILABLE_SYS_MEM_IN_BYTES / MEM_USED_PER_INSTANCE_IN_BYTES
        return max_threads
    except:
        return None

def get_thread_id():
    global thread_counter
    thread_counter += 1
    if not hasattr(thread_local, "id"):
        thread_local.id = thread_counter
    return thread_local.id





# psutil.cpu_times_percent

