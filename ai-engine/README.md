# 💎 MORAA GemVision — AI Engine

AI-powered jewellery image analysis engine for the MORAA GemVision platform.

## 🔬 Current Status

The AI analysis engines have been integrated directly into the **backend** at `backend/app/ai/`. Two engines are available:

| Engine | Description |
|---|---|
| **`mock`** | Returns random/placeholder analysis — ideal for frontend development |
| **`vision`** | PIL-based real image analysis (colour detection, clarity assessment, flaw detection) |

This directory is reserved for a standalone, more advanced AI engine (e.g., using TensorFlow, PyTorch, or a cloud vision API).

## 🧪 Planned Features

- Deep-learning-based gemstone classification
- Cut quality assessment from images
- Carat weight estimation
- Market value prediction
- Cloud-vision API integration

## 🔧 Usage

See the **backend** README for how to configure and plug in AI engines.
