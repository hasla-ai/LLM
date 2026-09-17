import argparse
import json
import random
from pathlib import Path

import torch
from torch.nn.utils import clip_grad_norm_

from .model import ForgeGPT


def load_text(path: Path):
    return "\n\n".join(json.loads(line)["text"] for line in path.read_text(encoding="utf-8").splitlines())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--context", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--out", type=Path, default=Path("artifacts/forge-gpt.pt"))
    args = parser.parse_args()
    text = load_text(args.data)
    alphabet = sorted(set(text))
    stoi = {char: index for index, char in enumerate(alphabet)}
    data = torch.tensor([stoi[char] for char in text], dtype=torch.long)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ForgeGPT(len(alphabet), context=args.context).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1)
    model.train()
    for step in range(args.steps):
        starts = [random.randrange(0, len(data) - args.context - 1) for _ in range(args.batch_size)]
        x = torch.stack([data[s:s + args.context] for s in starts]).to(device)
        y = torch.stack([data[s + 1:s + args.context + 1] for s in starts]).to(device)
        _, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % 100 == 0:
            print(f"step={step} loss={loss.item():.4f} device={device}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "vocab": alphabet, "context": args.context}, args.out)
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
