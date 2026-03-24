import socket
import json
import pybrood
from pybrood import bwapi

class TCPServerBot:
    def __init__(self, port=9999):
        self.port = port
        self.sock = None
        self.conn = None
        self.addr = None
        self.game = None
        self.player = None

    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(1)
        # We'll block until the Mac connects
        print(f"[TCP] Waiting for Mac connection on port {self.port}...")
        self.conn, self.addr = self.sock.accept()
        print(f"[TCP] Connect from {self.addr}")

    def onStart(self):
        self.game = bwapi.Broodwar
        self.player = self.game.self()
        self.game.sendText("TCP Server Bot Loaded!")
        # Start TCP server right after game starts
        if not self.conn:
            self.start_server()

    def serialize_state(self):
        units_data = []
        for unit in self.player.getUnits():
            units_data.append({
                "id": unit.getID(),
                "type": unit.getType().getName(),
                "x": unit.getPosition().x,
                "y": unit.getPosition().y,
                "health": unit.getHitPoints(),
                "is_training": unit.isTraining(),
                "idle": unit.isIdle()
            })
            
        minerals_data = []
        for unit in self.game.getMinerals():
            # In real scenario, filter minerals near start location
            minerals_data.append({
                "id": unit.getID(),
                "x": unit.getPosition().x,
                "y": unit.getPosition().y,
                "amount": unit.getResources()
            })

        state = {
            "frame": self.game.getFrameCount(),
            "minerals": self.player.minerals(),
            "gas": self.player.gas(),
            "supply_used": self.player.supplyUsed() // 2,
            "supply_total": self.player.supplyTotal() // 2,
            "units": units_data,
            "minerals_fields": minerals_data[:10]  # Just send a few for the basic script
        }
        return state

    def execute_actions(self, actions):
        for act in actions:
            action_type = act.get("action")
            unit_id = act.get("unit_id")
            
            unit = self.game.getUnit(unit_id)
            if not unit or not unit.exists():
                continue
                
            if action_type == "train":
                target_type_str = act.get("target_type")
                if target_type_str == "worker":
                    # Determine worker type
                    race = self.player.getRace()
                    worker_type = race.getWorker()
                    unit.train(worker_type)
                    
            elif action_type == "gather":
                target_id = act.get("target_id")
                target_mineral = self.game.getUnit(target_id)
                if target_mineral and target_mineral.exists():
                    unit.gather(target_mineral)

    def onFrame(self):
        if not self.conn:
            return

        state = self.serialize_state()
        try:
            # Send state
            state_json = json.dumps(state) + "\n"
            self.conn.sendall(state_json.encode('utf-8'))
            
            # Read commands (blocking, so the game pauses until Mac replies)
            # You might want to implement a timeout here if you don't want strict lockstep
            buffer = ""
            while '\n' not in buffer:
                data = self.conn.recv(4096).decode('utf-8')
                if not data:
                    print("[TCP] Mac disconnected.")
                    self.conn = None
                    return
                buffer += data
                
            line, _ = buffer.split('\n', 1)
            actions = json.loads(line)
            
            self.execute_actions(actions)
            
        except Exception as e:
            print(f"[TCP] Error during communication: {e}")
            self.game.pauseGame()
            self.conn = None

    def onEnd(self, isWinner):
        if self.conn:
            self.conn.close()
        if self.sock:
            self.sock.close()


if __name__ == "__main__":
    bot = TCPServerBot()
    # pybrood client loop setup here
    # Since pybrood API binds to the C++ events, we wrap it
    class PyBroodBot(pybrood.BaseAIModule):
        def onStart(self):
            bot.onStart()
        def onFrame(self):
            bot.onFrame()
        def onEnd(self, isWinner):
            bot.onEnd(isWinner)
            
    # pybrood.run(PyBroodBot) # pseudo code, adjust based on exact pybrood version
