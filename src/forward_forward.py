import torch
import torch.nn as nn
import torch.nn.functional as F


class BlockBase(nn.Module):
    def __init__(self, in_dim, out_dim, normalize_input, ff, bias=False):
        super().__init__()
        self.fc = nn.Linear(in_dim, out_dim, bias=bias)
        self.relu = nn.ReLU(True)
        self.normalize_input = normalize_input
        self.ff = ff

    def forward(self, x):
        if self.normalize_input:
            x = F.normalize(x, dim=1)
        
        x = self.fc(x)
        self.x = x

        if self.ff:
            return self.relu(x).detach()
        return self.relu(x)

class FFBase(nn.Module):
    def __init__(self, dims, ff=True):
        super().__init__()

        blocks = []
        blocks.append(BlockBase(dims[0], dims[1], False, ff))
        for i in range(len(dims[1:-1])):
            blocks.append(BlockBase(dims[i+1], dims[i+2], True, ff))
        
        # just for print
        self.blocks = nn.Sequential(*blocks)
        self.n_blocks = len(blocks)
        self.ff = ff

    def forward(self, x, cat=True):
        x = self.blocks(x)

        if not self.ff:
            return x
        
        xs = [b.x for b in self.blocks.children()]

        if not cat:
            return xs
        return torch.stack(xs, dim=1)
        
class BlockMLP(nn.Module):
    def __init__(self, in_dim, out_dim, normalize_input, ff, bias=False):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, out_dim, bias=bias)
        self.fc2 = nn.Linear(out_dim, out_dim, bias=bias)
        self.relu1 = nn.ReLU(True)
        self.relu2 = nn.ReLU(True)
        self.normalize_input = normalize_input
        self.ff = ff

    def forward(self, x):
        if self.normalize_input:
            x = F.normalize(x, dim=1)
        
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        self.x = x

        if self.ff:
            return self.relu2(x).detach()
        return self.relu2(x)

class FFMLP(nn.Module):
    def __init__(self, dims, ff=True):
        super().__init__()

        blocks = []
        blocks.append(BlockMLP(dims[0], dims[1], False, ff))
        for i in range(len(dims[1:-1])):
            blocks.append(BlockMLP(dims[i+1], dims[i+2], True, ff))
        
        # just for print
        self.blocks = nn.Sequential(*blocks)
        self.n_blocks = len(blocks)
        self.ff = ff

    def forward(self, x, cat=True):
        x = self.blocks(x)

        if not self.ff:
            return x
        
        xs = [b.x for b in self.blocks.children()]

        if not cat:
            return xs
        return torch.stack(xs, dim=1)