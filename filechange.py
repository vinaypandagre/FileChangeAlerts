import os
import hashlib
import requests
import time

def get_file_hashes(files, path):
    """Calculate MD5 hashes for a list of files"""
    hashes = {}
    for file in files:
        with open(os.path.join(path, file), 'rb') as f:
            data = f.read()
            hashes[file] = hashlib.md5(data).hexdigest()
    return hashes

def monitor_file_changes(path):
    """Monitor file changes in a directory"""
    old_state = get_file_hashes(os.listdir(path), path)
    while True:
        time.sleep(2)
        new_state = get_file_hashes(os.listdir(path), path)
        yield old_state, new_state
        old_state = new_state

def send_notification(message):
    """Send a notification to a URL"""
    try:
        requests.post("https://ntfy.sh/yourtopic", data=message.encode('utf-8')) #replace your topic with any name where you wnat to recieve the notification
    except requests.RequestException as e:
        print(f"Error sending notification: {e}")

def process_file_changes(old_state, new_state):
    """Process file changes and send notifications"""
    del_file = set(old_state.keys()) - set(new_state.keys())
    add_file = set(new_state.keys()) - set(old_state.keys())
    modified_files = []
    renamed_files = {}

    for file_path in del_file:
        for new_file_path, new_file_hash in new_state.items():
            if old_state[file_path] == new_file_hash:
                renamed_files[file_path] = new_file_path
                break

    for file_path, file_hash in new_state.items():
        if file_path in old_state and old_state[file_path]!= file_hash:
            modified_files.append(file_path)

    for file_path in del_file:
        if file_path not in renamed_files:
            send_notification(f"{file_path} file deleted")

    for file_path in add_file:
        if file_path not in renamed_files.values():
            send_notification(f"{file_path} file added")

    for file_path in modified_files:
        send_notification(f"{file_path} file modified")

    for old_path, new_path in renamed_files.items():
        send_notification(f"file {old_path} renamed to {new_path}")

if __name__ == "__main__":
    path = "/Users/panda/Desktop/test"
    for old_state, new_state in monitor_file_changes(path):
        process_file_changes(old_state, new_state)
