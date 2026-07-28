# Zenith — Local AI Security Scanner

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![TypeScript](https://img.shields.io/badge/typescript-5.4-blue)
![License](https://img.shields.io/badge/license-None-red)

> **Zenith** is a locally-run AI security scanner that detects hardcoded secrets and vulnerable dependencies in your codebase.

---

## Overview

Zenith is a DevSecOps tool built to reduce false positives in secret scanning. Traditional regex-based scanners flag every instance of strings like `password` or `api_key`, including harmless mock variables and test data. This creates alert fatigue and causes developers to ignore legitimate warnings.

Zenith addresses this by routing potential secrets through a lightweight, 3.8-billion parameter neural network (`microsoft/Phi-3-mini-4k-instruct`) running directly on local hardware. The model analyzes the surrounding code context to determine whether a string is a live production credential or test data — without sending any code off-device.

## Why This Project?

Alert fatigue is a real problem in software security. When scanners generate too many false positives, developers stop trusting them, and real leaks go undetected. Zenith is designed to be accurate enough to take seriously, and private enough to use without policy concerns.

## Key Features

- **Local AI Secret Scanning:** Detects AWS keys, GitHub tokens, Stripe keys, and other common credential formats.
- **Context-Aware False Positive Reduction:** Uses an LLM to distinguish between a live credential and a clearly fake test value.
- **Hardware Acceleration:** Runs natively on Apple Silicon (MPS/Neural Engine), AMD XDNA, or Intel NPU via ONNX Runtime.
- **Dependency Vulnerability Auditing:** Cross-references `requirements.txt`, `package.json`, and other manifests against the Open Source Vulnerabilities (OSV) database to surface known CVEs.
- **Live IDE Integration:** A VS Code extension connects to a local FastAPI server and highlights secrets as you type.
- **Pre-commit Hooks:** Blocks commits containing live secrets before they reach Git history.

## Tech Stack

- **Core and CLI:** Python (3.10+), `click`, `rich`
- **Machine Learning Engine:** `torch`, `transformers`, `accelerate`, `onnxruntime`
- **Background API:** `fastapi`, `uvicorn`, `requests`
- **IDE Extension:** TypeScript, VS Code API, `esbuild`, `axios`

## Architecture

Zenith is composed of four modular components:

1. **CLI (`zenith.cli`)** — Provides `zenith scan` and `zenith audit` commands for manual invocation.
2. **Server (`zenith.server`)** — A FastAPI application that runs in the background and exposes a `/scan` endpoint.
3. **VS Code Extension (`zenith-vscode`)** — A TypeScript plugin that monitors the active editor and sends text to the local server for analysis.
4. **AI Engine (`zenith.ai.inference`)** — A singleton that loads and caches the LLM in local memory (RAM or VRAM) for low-latency inference.

## Prerequisites

- Python 3.10 or later
- Node.js 20.x (required only if building the VS Code extension from source)
- Git
- Hardware:
  - macOS: Apple Silicon (M1/M2/M3/M4) is recommended for MPS acceleration.
  - Windows/Linux: Requires the INT4 quantized ONNX model for CPU or NPU acceleration.

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/Cy-nape/ZENITH-V2.0.git
cd ZENITH-V2.0
```

**2. Create and activate a Python virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**3. Install the Zenith package and its dependencies**

```bash
pip install -e .
```

**4. Build the VS Code extension** (optional, only needed for IDE integration)

```bash
cd zenith-vscode
npm install
npm run build
cd ..
```

## Environment Variables

Zenith requires no external API keys or environment variables. All AI inference runs locally on your machine.

## Usage

### Command Line

Scan a single file using regex only:

```bash
zenith scan path/to/file.py
```

Scan a file with AI-assisted context analysis:

```bash
zenith scan path/to/file.py --ai --profile
```

Audit project dependencies against the OSV database:

```bash
zenith audit .
```

### Live IDE Integration

To run the VS Code extension in development mode:

1. Start the Zenith backend server:

   ```bash
   python -m zenith.server
   ```

   The server listens on `http://127.0.0.1:8765`.

2. Open the `zenith-vscode` folder in VS Code.
3. Press **F5** to launch the Extension Development Host.
4. In the new VS Code window, open any file and type a credential-like string, for example:

   ```
   api_key = "sk_livefake_1234567890abcdefghijklmn"
   ```

   The extension will underline the value with a red diagnostic warning as you type.

## Running Tests

Unit tests are in the `tests/` directory and can be run with Python's built-in test runner:

```bash
python -m unittest discover -s tests
```

## Known Limitations

- **Model size:** When not running in demonstration mode, the first execution of `--ai` will download the `microsoft/Phi-3-mini-4k-instruct` model (~3.8 GB). Ensure sufficient disk space and a stable network connection.
- **Memory requirements:** Running a 3.8-billion parameter model locally requires significant RAM. At least 16 GB of unified memory is recommended on Apple Silicon devices.
- **Demonstration mode:** `zenith/ai/inference.py` currently contains hardcoded mock logic that simulates AI responses instantly without downloading the full model. To use the real AI, remove the `MOCK_SESSION` override in that file.

## Troubleshooting

**`command not found: zenith`**
Confirm that you ran `pip install -e .` and that your virtual environment is active.

**`ModuleNotFoundError: No module named 'torch'`**
Dependencies did not install correctly. Re-run `pip install -e .` from the project root.

**Slow AI inference on Mac**
Verify that your Python installation was compiled for ARM64 so PyTorch can use the Apple MPS (Metal Performance Shaders) backend.

## Project Structure

```text
.
├── zenith/                 # Core Python package
│   ├── ai/                 # Local LLM inference engine
│   ├── scanner/            # Regex extractors and CVE auditing logic
│   ├── hooks/              # Git pre-commit hook integration
│   ├── cli.py              # Click CLI entrypoint
│   └── server.py           # FastAPI background server
├── zenith-vscode/          # TypeScript VS Code extension
├── tests/                  # Unit tests
├── pyproject.toml          # Python package configuration and dependencies
└── DEMO.md                 # Live demonstration script
```

## License

No LICENSE file is currently included in this repository. Consider adding an open-source license (MIT or Apache 2.0) to clarify usage rights for contributors and visitors.
