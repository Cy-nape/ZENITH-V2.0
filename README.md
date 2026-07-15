# 🚀 Zenith - Local AI Security Scanner

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![TypeScript](https://img.shields.io/badge/typescript-5.4-blue)
![License](https://img.shields.io/badge/license-None-red)

> **Zenith** is a blazingly fast, locally-run AI security scanner that detects hardcoded secrets and vulnerable dependencies in your codebase.

---

## 📖 Overview

Zenith is a modern DevSecOps tool designed to eliminate the single biggest annoyance of standard security scanners: **False Positives**. Traditional regex-based scanners flag every instance of the word "password" or "api_key", forcing developers to sift through hundreds of harmless mock variables and test data.

Zenith solves this by routing potential secrets through a lightweight, 3.8-Billion parameter Neural Network (`microsoft/Phi-3-mini-4k-instruct`) **running directly on your local hardware**. It semantically analyzes the context of the code to determine if a string is a live production credential or just harmless test data—all while ensuring your code never leaves your laptop.

## 🎯 Why This Project?

Alert fatigue is a massive problem in software engineering. When security tools cry wolf too often, developers start ignoring them, leading to catastrophic leaks. Zenith provides context-aware, highly accurate security auditing without compromising on privacy or execution speed.

## ✨ Key Features

- **Local AI Secret Scanning:** Detects AWS keys, GitHub tokens, Stripe keys, and more.
- **Context-Aware False Positive Filtration:** Uses an LLM to distinguish between `sk_live_123` and `fake_test_key`.
- **Hardware Accelerated:** Runs natively on Apple Silicon (MPS Neural Engine), AMD XDNA, or Intel NPU via ONNX Runtime.
- **Dependency Vulnerability Auditing:** Cross-references `requirements.txt`, `package.json`, and other manifests against the Open Source Vulnerabilities (OSV) database to catch Critical CVEs instantly.
- **Live IDE Integration:** A VS Code extension connects to a local FastAPI server to highlight secrets as you type.
- **Pre-commit Hooks:** Blocks commits containing live secrets before they ever reach Git.

## 🛠 Tech Stack

- **Core & CLI:** Python (3.10+), `click`, `rich`
- **Machine Learning Engine:** `torch`, `transformers`, `accelerate`, `onnxruntime`
- **Background API:** `fastapi`, `uvicorn`, `requests`
- **IDE Extension:** TypeScript, `vscode` API, `esbuild`, `axios`

## 🏗 Architecture

Zenith operates through modular components:
1. **The CLI (`zenith.cli`)**: Provides manual commands like `zenith scan` and `zenith audit`.
2. **The Server (`zenith.server`)**: A background FastAPI application exposing a `/scan` endpoint.
3. **The Extension (`zenith-vscode`)**: A TypeScript plugin that watches your keystrokes and pings the local server.
4. **The AI Engine (`zenith.ai.inference`)**: A singleton class that caches the LLM in local memory (RAM/VRAM) to achieve sub-second inference latency.

## 🚦 Prerequisites

Before installing Zenith, ensure you have the following:
- **Python 3.10+** installed
- **Node.js 20.x** (Required only for building the VS Code extension)
- **Git**
- **Hardware Requirements:**
  - Mac: Apple Silicon (M1/M2/M3/M4) is highly recommended for MPS acceleration.
  - Windows/Linux: Requires downloading the INT4 Quantized ONNX model manually for CPU/NPU acceleration.

## 💻 Installation

Follow these steps to set up the project locally:

**1. Clone the repository**
```bash
git clone https://github.com/Cy-nape/ZENITH-V2.0.git
cd ZENITH-V2.0
```

**2. Set up the Python Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

**3. Install the Zenith CLI and Python Dependencies**
```bash
pip install -e .
```

**4. Build the VS Code Extension**
```bash
cd zenith-vscode
npm install
npm run build
cd ..
```

## ⚙️ Environment Variables

Zenith requires **no external API keys** or environment variables for its core secret scanning because all AI inference happens 100% locally on your machine.

## 🚀 Running the Project

### Command Line Interface

**1. Scan a file for secrets (Regex Only)**
```bash
zenith scan path/to/file.py
```

**2. Scan a file using the Local AI Engine**
```bash
zenith scan path/to/file.py --ai --profile
```

**3. Audit Project Dependencies**
```bash
zenith audit .
```

### Live IDE Integration

To use the "as-you-type" VS Code extension:

1. Start the Zenith backend server in a terminal:
   ```bash
   python -m zenith.server
   ```
   *(The server will start on `http://127.0.0.1:8765`)*
2. Open the `zenith-vscode` folder in VS Code.
3. Press **F5** to launch the Extension Development Host.
4. Open any file in the new window and type a secret (e.g., `api_key = "sk_livefake_1234567890abcdefghijklmn"`). You will immediately see a red warning underline.

## 🧪 Running Tests

Unit tests are located in the `tests/` directory. You can run them using Python's built-in `unittest` module:

```bash
python -m unittest discover -s tests
```

## ⚠️ Warnings / Known Limitations

- **Model Download Size:** If the AI is not running in "Mock" mode, the first time you run `--ai`, Zenith will download the `microsoft/Phi-3-mini-4k-instruct` model (~3.8GB). Ensure you have sufficient disk space and a stable internet connection.
- **Memory Usage:** Running a 3.8B parameter model locally requires significant RAM. It is recommended to have at least 16GB of Unified Memory on Macs.
- **Demonstration Mode:** Currently, `zenith/ai/inference.py` contains hardcoded mock logic to instantly simulate AI responses for presentation purposes without downloading the full model. To use the true AI, remove the `MOCK_SESSION` override in that file.

## 🛠 Troubleshooting

- **Error: `command not found: zenith`**
  Ensure that you ran `pip install -e .` and that your virtual environment is currently active.
- **Error: `ModuleNotFoundError: No module named 'torch'`**
  The dependencies did not install correctly. Run `pip install -r pyproject.toml` (or `pip install -e .`).
- **Mac Users - AI Latency is slow:**
  Ensure your Python installation was compiled with ARM64 support so PyTorch can hook into the Apple MPS (Metal Performance Shaders) backend.

## 📂 Project Structure

```text
├── zenith/                 # Core Python Package
│   ├── ai/                 # Local LLM Inference Engine
│   ├── scanner/            # Regex Extractors and CVE Auditing logic
│   ├── hooks/              # Git Pre-commit Hooks
│   ├── cli.py              # Click CLI Entrypoint
│   └── server.py           # FastAPI Background Server
├── zenith-vscode/          # TypeScript VS Code Extension
├── tests/                  # Unit tests
├── pyproject.toml          # Python package config & dependencies
└── DEMO.md                 # Live presentation script
```

## 📄 License

Currently, **no LICENSE file is included** in this repository. 
*(Maintainer Note: Consider adding an open-source license such as MIT or Apache 2.0 to clarify usage rights for visitors and contributors).*
