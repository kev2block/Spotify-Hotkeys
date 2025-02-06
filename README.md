# Spotify Hotkeys

This program is a desktop application that allows users to control Spotify playback using custom hotkeys. It features a system tray icon for easy access with Windows. The application provides quick controls for play/pause, skip, rewind, and volume adjustments.

![Alt text](/SpotifyHotkey/img/Screenshot.png?raw=true "Screenshot")


## Setup

### Prerequisites
(You need Spotify Premium)
1. Download the `requirements.txt` file and place it in your project directory.
2. Open Terminal and run:
    ```sh
    pip install -r requirements.txt
    ```

3. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create an app.
4. Name your app and provide a description.
5. In the **Redirect URIs** section, type: `http://localhost:8080/callback` and click "Add".
6. Under "*Which API/SDKs are you planning to use?*", select "**Web API**".
7. Save your app and navigate to the *Settings* at the top right corner.
8. Copy the `Client ID`, click *view client secret*, and copy the `Client Secret`.
9. Paste both the `Client ID` and `Client Secret` into the script.

### Create Desktop Application
1. Install PyInstaller by running:
    ```sh
    pip install pyinstaller
    ```

2. Create a standalone executable by running:
    ```sh
    pyinstaller --onefile --windowed SpotifyHotkey.py
    ```

3. After the process completes, a folder named `dist` will be created. Your `SpotifyHotkey.exe` file will be inside this folder.
4. Drag the `SpotifyHotkey.exe` file to your desktop and open it.
5. If your antivirus software blocks the file, allow the file through your antivirus settings and recreate the executable using:
    ```sh
    pyinstaller --onefile --windowed SpotifyHotkey.py
    ```
