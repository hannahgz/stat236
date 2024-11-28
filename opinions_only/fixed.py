import time
import requests
import pickle
from functools import wraps
from typing import Callable
import random
import os
import glob

def retry_with_backoff(max_retries: int = 15, initial_delay: float = 2) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            
            # Cloudflare and rate limit error codes
            RETRY_CODES = {
                408: "Request Timeout",
                429: "Rate limit exceeded",
                500: "Internal Server Error",
                502: "Bad Gateway",
                503: "Service Unavailable",
                504: "Gateway Timeout",
                520: "Unknown error",
                521: "Web server is down",
                522: "Connection timed out",
                523: "Origin is unreachable",
                524: "A timeout occurred",
                525: "SSL handshake failed",
                526: "Invalid SSL certificate",
                527: "Railgun error",
                530: "Site is frozen",
            }
            
            while retries < max_retries:
                try:
                    print("Trying function")
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as err:
                    status_code = err.response.status_code
                    if status_code in RETRY_CODES:
                        sleep_time = delay * (2 ** retries) + random.uniform(0, 1)
                        error_msg = RETRY_CODES.get(status_code, "Unknown error")
                        print(f"Status {status_code} ({error_msg}). "
                              f"Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                    else:
                        print(f"HTTP error occurred: {err}")
                        raise
                except Exception as e:
                    print(f"Error occurred: {e}")
                    sleep_time = delay * (2 ** retries) + random.uniform(0, 1)
                    print(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                
                retries += 1
            
            raise Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator


@retry_with_backoff(max_retries=50, initial_delay=2)
def make_api_request(url: str, headers: dict, params={}) -> dict:
    print("Trying URL: ", url)
    response = requests.get(url, headers=headers, params=params, timeout=(10,60))
    response.raise_for_status()
    return response.json()



# base_url = "https://www.courtlistener.com/api/rest/v4/opinions/"
# params = {
#     "court": "scotus",  # Filter for SCOTUS cases
#     "fields": "id",     # Only fetch the 'id' field
# }
params = {
    "cluster__docket__court": "scotus",  # Filter for SCOTUS cases
    "date_filed__gte": "1950-01-01",    # Filter for cases filed after 1950
    "fields": "id,cluster_id",                     # Only fetch the 'id' field
}



# pickle_files = glob.glob("checkpoints_fixed/scotus_ids_*.pkl")
# if pickle_files:
#     latest_file = max(pickle_files)
#     print(f"Loading: {latest_file}")
    
#     # Find the corresponding URL file
#     parts = latest_file.split('_')
#     timestamp = f"{parts[-3]}_{parts[-2]}"  # Combines date_time parts
#     print("timestamp: ", timestamp)
#     url_file = glob.glob(f"checkpoints_fixed/next_url_{timestamp}_*.txt")[0]
#     print("Loading URL: ", url_file)
#     with open(url_file, 'r') as f:
#         base_url = f.read().strip()

base_url = "https://www.courtlistener.com/api/rest/v4/opinions/"

# Replace with your actual API key
# Put your CourtListener API key here
api_key = "80e9ea74585c372bc72c0c9247852286d4a521fb"

headers = {
    # Authorization header with the API key
    "Authorization": f"Token {api_key}"
}

scotus_ids = []  # List to store SCOTUS case IDs
cluster_ids = []  # List to store SCOTUS case cluster IDs
MAX_REQUESTS = 4500  # Max requests per hour for authenticated users
TIME_WINDOW = 3600  # 1 h
request_count = 0  # Number of requests made in the current period
start_time = time.time()
CHECKPOINT_DIR = "checkpoints_new"
CHECKPOINT_FREQUENCY = 100  # Save every 100 requests
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def save_checkpoint(next_url: str, ids_list: list, cluster_ids_list: list, request_num: int):
    """Save checkpoint files with timestamp and request number."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Save next URL
    if next_url:
        url_file = os.path.join(CHECKPOINT_DIR, f"next_url_{timestamp}_{request_num}.txt")
        with open(url_file, "w") as f:
            f.write(next_url)
    
    # Save IDs list
    ids_file = os.path.join(CHECKPOINT_DIR, f"scotus_ids_{timestamp}_{request_num}.pkl")
    with open(ids_file, "wb") as f:
        pickle.dump(ids_list, f)
    
    # Save cluster IDs list
    cluster_ids_file = os.path.join(CHECKPOINT_DIR, f"cluster_ids_{timestamp}_{request_num}.pkl")
    with open(cluster_ids_file, "wb") as f:
        pickle.dump(cluster_ids_list, f)
    
    # Keep only the 5 most recent checkpoints
    cleanup_old_checkpoints()

def cleanup_old_checkpoints(keep_num: int = 5):
    """Remove old checkpoint files, keeping only the most recent ones."""
    for file_pattern in ["next_url_*.txt", "scotus_ids_*.pkl", "cluster_ids_*.pkl"]:
        files = glob.glob(os.path.join(CHECKPOINT_DIR, file_pattern))
        files.sort(reverse=True)  # Sort by filename (which includes timestamp)
        for old_file in files[keep_num:]:
            os.remove(old_file)

# def load_latest_checkpoint():
#     """Load the most recent checkpoint files."""
#     # Find most recent scotus_ids file
#     ids_files = glob.glob(os.path.join(CHECKPOINT_DIR, "scotus_ids_*.pkl"))
#     if not ids_files:
#         return None, []
    
#     latest_ids_file = max(ids_files)
#     timestamp = latest_ids_file.split("_")[-2]  # Extract timestamp
    
#     # Load IDs
#     with open(latest_ids_file, "rb") as f:
#         scotus_ids = pickle.load(f)
    
#     # Find corresponding URL file
#     url_file = os.path.join(CHECKPOINT_DIR, f"next_url_{timestamp}_*.txt")
#     url_files = glob.glob(url_file)
#     next_url = None
#     if url_files:
#         with open(url_files[0], "r") as f:
#             next_url = f.read().strip()
    
#     return next_url, scotus_ids


base_url = "https://www.courtlistener.com/api/rest/v4/opinions/?cluster__docket__court=scotus&cursor=cD04NTk4Mg%3D%3D&date_filed__gte=1950-01-01&fields=id%2Ccluster_id"

total_requests = 0
while base_url:
    print(f"Starting request {request_count + 1} to {base_url}")

    # For the first request only
    if '?' not in base_url:  # Check if URL already has parameters
        data = make_api_request(base_url, headers, params)
    else:
        data = make_api_request(base_url, headers, {})  # Empty params for subsequent requests

    request_count += 1
    total_requests += 1

    scotus_ids.extend(item['id'] for item in data["results"])
    cluster_ids.extend(item['cluster_id'] for item in data["results"])
    print(f"Requests made: {total_requests}")

    # Rate limit handling
    if request_count >= MAX_REQUESTS:
        elapsed_time = time.time() - start_time
        if elapsed_time < TIME_WINDOW:
            sleep_duration = TIME_WINDOW - elapsed_time + random.uniform(1, 5)
            print(f"Rate limit approaching. Sleeping for {sleep_duration:.2f} seconds.")
            time.sleep(sleep_duration)
        
        request_count = 0
        start_time = time.time()

    base_url = data.get('next')
    print("base_url: ", base_url)
    
    # Save checkpoint every CHECKPOINT_FREQUENCY requests
    if request_count % CHECKPOINT_FREQUENCY == 0:
        save_checkpoint(base_url, scotus_ids, cluster_ids, total_requests)

# Save final checkpoint
save_checkpoint(base_url, scotus_ids, cluster_ids, total_requests)
