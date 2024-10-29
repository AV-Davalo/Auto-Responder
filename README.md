## How It Works
### User Input
- Start time: Time to start the first Responder session (e.g., 08:00).
- Run duration: How many minutes to run Responder in each session (e.g., 30 minutes).
- Wait time: How long to wait between stopping Responder and starting the next session (e.g., 60 minutes).
- End time: The time at which the script will stop starting new sessions for the day (e.g., 18:00).
### Loop Control
The script will keep running sessions until the end time is reached.
Each session will run for the user-defined duration, stop, wait for the specified period, and then start again.
When the end time passes, no more sessions will be started, and a notification will be sent to indicate that the day's schedule is complete.
### Notifications
Pushover notifications are sent when:
Responder starts.
Responder stops.
The daily schedule is completed.
### Example Scenario
- Start time: 08:00
- Run duration: 30 minutes
- Wait time: 60 minutes
- End time: 18:00
### Behavior:
Responder starts at 08:00, runs for 30 minutes, and stops at 08:30.
It waits for 60 minutes, starts again at 09:30, runs for 30 minutes, and stops at 10:00.
This cycle repeats until 18:00, after which no more sessions will start, and the script stops.
Additional Features
Log monitoring is included within each session to check for captured NTLMv2 hashes, and a notification will be sent if any are found.
