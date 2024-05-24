# Spotify-Hotkeys
- This program is a desktop application that allows users to control Spotify playback using custom hotkeys. It features a system tray icon for easy access and supports autostart with Windows. The application provides quick controls for play/pause, skip, rewind, and volume adjustments.


## Setup

### Prerequisites
- Download "requirements.txt" and put it in your project. In Terminal type: `pip install -r requirements.txt`
- 
- Go to the [Spotify Dashboard](https://developer.spotify.com/dashboard) and create a app.
- Name your App and give it a description.
- In **Redirect URIs** type: `http://localhost:8080/callback` and click "Add".
- At "*Which API/SDKs are you planning to use?*", click "**Web API**"
- Then save your app and go to *Settings* at the top right corner.
- Copy the `Client ID`, click *view client secret* and copy the `Client secret`.
- Paste both of them in the script.

### Create Desktop application
- In Terminal type `pip install pyinstaller`
- Then type `pyinstaller --onefile --windowed SpotifyHotkey.py`
- After this a folder named *"dist"* will be created, where your `SpotifyHotkey.exe` file is in.
- Drag the file on the desktop and open it.
- If your "antivirus software" blocks the file, just allow the file and create the .exe file again with `pyinstaller --onefile --windowed SpotifyHotkey.py`
