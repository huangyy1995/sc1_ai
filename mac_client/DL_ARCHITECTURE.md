# Deep Learning Architecture Guide for MacOS

Now that the `mac_client/bot_client.py` receives a JSON state and sends JSON actions every frame, you have a perfect decoupled environment. This means the MacBook doesn't need to know anything about C++ or BWAPI, making it the ideal host for PyTorch.

## 1. Environment Setup

Install PyTorch on the MacBook:
```bash
pip install torch torchvision numpy
```

## 2. Converting Game State to Tensors

In the `bot_client.py` you currently have a `process_state(state)` method. Instead of scripting the logic, you can feed the state to a Neural Network. 
You first need to transform the custom `units` and `minerals_fields` list into a fixed-size or graph-based tensor format.

### Option A: Fixed-sized Spatial Grids (Like AlphaStar)
Create a spatial representation of the map where each channel is a feature (e.g. Channel 1 = my units, Channel 2 = enemy units, Channel 3 = mineral patches).

```python
import torch
import numpy as np

def state_to_tensor(state, map_size=(256, 256)):
    grid = np.zeros((3, map_size[0], map_size[1]), dtype=np.float32)
    # Channel 0: Minerals, Channel 1: My Units
    for m in state.get("minerals_fields", []):
         # Scale down coordinates to fit grid
         x, y = m["x"] // 8, m["y"] // 8 
         grid[0, y, x] = 1.0
         
    for u in state.get("units", []):
         x, y = u["x"] // 8, u["y"] // 8
         grid[1, y, x] = 1.0
         
    return torch.from_numpy(grid).unsqueeze(0) # Shape: [1, 3, 256, 256]
```

### Option B: Graph Neural Networks (GNN)
Represent every unit as a node in a graph. Pass the data through `torch_geometric` modules to process an arbitrary number of units.

## 3. The Model Architecture

A basic Reinforcement Learning (RL) actor-critic model or a behavioral cloning model:
```python
import torch.nn as nn
import torch.nn.functional as F

class StarCraftBrain(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1)
        self.fc1 = nn.Linear(32 * 128 * 128, 256)
        
        # Policy head (e.g. action probabilities)
        self.policy_head = nn.Linear(256, 10) 
        
        # Value head (for RL)
        self.value_head = nn.Linear(256, 1)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        policy_logits = self.policy_head(x)
        value = self.value_head(x)
        return policy_logits, value
```

## 4. Hooking the Neural Net to the TCP Protocol

Update the `MacBotClient` logic to instantiate the brain:

```python
# Insert this in bot_client.py
from model import StarCraftBrain, state_to_tensor
import torch

brain = StarCraftBrain()
# optionally load weights: brain.load_state_dict(torch.load('model.pth'))

def process_state(self, state):
    tensor_state = state_to_tensor(state)
    
    with torch.no_grad():
        logits, value = brain(tensor_state)
        action_idx = torch.distributions.Categorical(logits=logits).sample().item()
        
    # Map action_idx back to JSON payload
    actions = []
    if action_idx == 0:
        actions.append({"action": "train", "unit_id": ...})
    # ...
    return actions
```

## 5. Training Loop
For RL training, you would likely need to run multiple instances of the game headless without chaoslauncher, or run thousands of replays using `bwapi` replay data. However, as an initial start, creating a simple behavior cloning model or online learning bot running against the built-in AI will serve as a strong baseline using this exact TCP setup!
