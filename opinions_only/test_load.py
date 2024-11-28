import glob
import os
import pickle

# Find most recent pickle file
pickle_files = glob.glob("checkpoints/scotus_ids_*.pkl")
if pickle_files:
    latest_file = max(pickle_files)  # Gets the last file alphabetically (which will be the most recent due to timestamp)
    print(f"Loading: {latest_file}")
    
    with open(latest_file, 'rb') as file:
        scotus_ids = pickle.load(file)
        
    print(f"Total IDs: {len(scotus_ids)}")
    print(f"First 5 IDs: {scotus_ids[:5]}")
else:
    print("No pickle files found")



# Find most recent pickle file
pickle_files = glob.glob("checkpoints/cluster_ids_*.pkl")
if pickle_files:
    latest_file = max(pickle_files)  # Gets the last file alphabetically (which will be the most recent due to timestamp)
    print(f"Loading: {latest_file}")
    
    with open(latest_file, 'rb') as file:
        scotus_ids = pickle.load(file)
        
    print(f"Total IDs: {len(scotus_ids)}")
    print(f"First 5 IDs: {scotus_ids[:5]}")
else:
    print("No pickle files found")
