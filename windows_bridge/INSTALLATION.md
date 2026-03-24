# Installation & Setup on Windows Machine

To use the Windows machine as the execution environment for StarCraft: Brood War and BWAPI, follow these precise steps.

## Prerequisites
1. **StarCraft: Brood War (Version 1.16.1)**
   - BWAPI only supports SC:BW version 1.16.1 (not the modern Remastered version).
   - Ensure the game is installed in a directory like `C:\StarCraft`.
2. **BWAPI (Brood War API)**
   - Download the latest BWAPI release (e.g., v4.4.0) from the official GitHub repository.
   - Run the installer.
3. **Chaoslauncher**
   - Download Chaoslauncher (often included with BWAPI or found online).
   - Place it in your StarCraft directory.

## Python Setup
On the Windows machine:
1. Install Python 3.8+ (make sure to select "Add Python to PATH" during installation).
2. Open a command prompt (`cmd`) or PowerShell.
3. Copy this `windows_bridge` folder to your Windows machine.
4. Navigate into the folder: `cd path\to\windows_bridge`
5. Install `pybrood`: `pip install -r requirements.txt`

## Running the Setup
1. Open **Chaoslauncher** as an Administrator.
2. In Chaoslauncher, check both `BWAPI Injector [...]` and `W-MODE` (for windowed mode).
3. Open `bwapi.ini` (usually situated inside `C:\StarCraft\bwapi-data\`)
   - Find the section `[ai]`
   - Set `ai = ` to empty because we are running Python, or configure pybrood loader. Actually, `pybrood` runs externally and injects itself, so you might just leave `ai` unconfigured.
4. Open a command prompt and run the Python script:
   ```cmd
   python tcp_server_bot.py
   ```
   *The terminal should say `[TCP] Waiting for Mac connection on port 9999...`*

5. Finally, launch StarCraft from Chaoslauncher. Start a single-player game or a Local Area Network game.
   - As soon as the game begins (`onStart` is triggered), the BWAPI hook will engage.
   - The Windows firewall may prompt you to allow Python through; please **allow** it on Private Networks.

## Connecting from the Mac
Once the Windows server says it is waiting, on your MacBook, navigate to the `mac_client` folder and run:
```bash
python bot_client.py --ip <YOUR_WINDOWS_IP_ADDRESS>
```
The two machines are now communicating in lockstep over TCP/JSON!
