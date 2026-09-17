import torch
from torch import nn


class CausalSelfAttention(nn.Module):
    def __init__(self, dim: int, heads: int, dropout: float):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, heads, dropout=dropout, batch_first=True)
        self.register_buffer("mask", torch.triu(torch.ones(1024, 1024), diagonal=1).bool())

    def forward(self, x):
        length = x.size(1)
        y, _ = self.attn(x, x, x, attn_mask=self.mask[:length, :length], need_weights=False)
        return y


class Block(nn.Module):
    def __init__(self, dim: int, heads: int, dropout: float):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = CausalSelfAttention(dim, heads, dropout)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(nn.Linear(dim, 4 * dim), nn.GELU(), nn.Linear(4 * dim, dim), nn.Dropout(dropout))

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        return x + self.mlp(self.norm2(x))


class ForgeGPT(nn.Module):
    def __init__(self, vocab_size: int, context: int = 256, dim: int = 256, heads: int = 4, layers: int = 4, dropout: float = 0.1):
        super().__init__()
        self.context = context
        self.token = nn.Embedding(vocab_size, dim)
        self.position = nn.Embedding(context, dim)
        self.blocks = nn.Sequential(*[Block(dim, heads, dropout) for _ in range(layers)])
        self.norm = nn.LayerNorm(dim)
        self.lm_head = nn.Linear(dim, vocab_size, bias=False)
        self.lm_head.weight = self.token.weight

    def forward(self, ids, targets=None):
        length = ids.size(1)
        positions = torch.arange(length, device=ids.device)
        x = self.token(ids) + self.position(positions)
        logits = self.lm_head(self.norm(self.blocks(x)))
        loss = None
        if targets is not None:
            loss = nn.functional.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        return logits, loss
