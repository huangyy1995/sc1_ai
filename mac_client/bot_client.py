import socket
import json
import time

class MacBotClient:
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while not self.connected:
            try:
                print(f"Connecting to Windows bridge at {self.host}:{self.port}...")
                self.sock.connect((self.host, self.port))
                self.connected = True
                print("Connected successfully!")
            except ConnectionRefusedError:
                print("Connection refused. Retrying in 2 seconds...")
                time.sleep(2)

    def process_state(self, state):
        """
        Simple Scripted Logic (e.g., Worker Mining)
        State is a dict representing the game state.
        Returns a list of actions to perform.
        """
        actions = []
        my_units = state.get("units", [])
        minerals_fields = state.get("minerals_fields", [])

        minerals = state.get("minerals", 0)

        # 1. Train workers
        for unit in my_units:
            if "Command_Center" in unit["type"] or "Nexus" in unit["type"] or "Hatchery" in unit["type"]:
                if unit["idle"] and minerals >= 50:
                    actions.append({"action": "train", "unit_id": unit["id"], "target_type": "worker"})
                    minerals -= 50 # deduct locally to prevent double training in same frame

            # 2. Command idle workers to mine
            if "SCV" in unit["type"] or "Probe" in unit["type"] or "Drone" in unit["type"]:
                if unit["idle"] and len(minerals_fields) > 0:
                    # Pick the first mineral field for simplicity
                    target_mineral = minerals_fields[0]["id"]
                    actions.append({"action": "gather", "unit_id": unit["id"], "target_id": target_mineral})

        return actions

    def run(self):
        self.connect()
        buffer = ""
        try:
            while True:
                # Read from socket until newline
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    print("Server closed connection.")
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line.strip():
                        continue
                    
                    try:
                        state = json.loads(line)
                        actions = self.process_state(state)
                        
                        # Send actions back
                        response = json.dumps(actions) + "\n"
                        self.sock.sendall(response.encode('utf-8'))
                        
                        if state.get("frame", 0) % 100 == 0:
                            print(f"Processed frame {state.get('frame')}")
                            
                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON: {line}")
                        
        except KeyboardInterrupt:
            print("Bot stopped by user.")
        finally:
            self.sock.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="StarCraft Mac AI Client")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address of the Windows machine")
    parser.add_argument("--port", type=int, default=9999, help="Port of the Windows TCP Server")
    args = parser.parse_args()
    
    bot = MacBotClient(host=args.ip, port=args.port)
    bot.run()
