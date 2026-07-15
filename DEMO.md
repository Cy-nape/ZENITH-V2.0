# 🚀 Zenith Demo Script (For Judges & Clients)

This is a step-by-step script intentionally designed to **"wow"** judges by visually demonstrating Zenith's speed, context-aware AI filtration, and local privacy!

---

## 🛠️ Prep (Perform before the demo starts)
Ensure your environment is set up and your virtual environment is active in your terminal.
1. Open up VS Code to your `Zenith` project.
2. Open a terminal and run: `source .venv/bin/activate`

---

## 🎬 Act 1: The Core AI Scanner (False Positive Filtration)

**The Setup:** You want to show that regular security scanners generate "false positives" (flagging test code), but Zenith is smart enough to ignore test code using its local M4 AI.

**The Action:**
1. Create a dummy file named `demo.py` and paste the following code:
```python
import os

# Example 1: A harmless test password
password = "test_password_123"

# Example 2: A REAL AWS Key!
aws_secret_key = "AKIAIOSFODNN7EXAMPLE12"
```
2. **First, scan normally:** Run `zenith scan demo.py`
   > *Point out to the judges*: "Notice how standard regex flags BOTH, even though the first one is just a harmless test string."
3. **Now, scan with AI:** Run `zenith scan demo.py --ai --profile`
   > *Point out to the judges*: "Now watch. Zenith routes the code through a local 3.8-Billion parameter Neural Network directly into the Mac M4 chip. It instantly realizes the first one is a test variable and hides it, while reporting the real AWS key—all in milliseconds!"

---

## 🎬 Act 2: The Security Audit (OSV Dependency Auditing)

**The Setup:** Explain that Zenith isn't just for secrets; it protects the entire infrastructure from Zero-Day vulnerabilities.

**The Action:**
1. Open your `requirements.txt` file and add this outdated library at the top:
```text
requests==2.20.0
```
2. **Run the Audit:** Run `zenith audit .`
3. A beautiful, vibrant Red and Magenta table will instantly appear!
   > *Point out to the judges*: "Instead of taking minutes to scan dependencies, Zenith natively maps our architecture against the Open Source Vulnerabilities Database and flags Critical CVEs with sub-second latency."

---

## 🎬 Act 3: Live IDE Integration (The "As-You-Type" Extension)

**The Setup:** Explain that developers hate using the CLI. You built Zenith directly into their workflow so they can't make mistakes.

**The Action:**
1. **Start the API Server:** In a background terminal, run: `python -m zenith.server` (Keep this running!)
2. Open the `zenith-vscode/src/extension.ts` file in VS Code.
3. Press **F5** on your keyboard. This will launch a new "Extension Development Host" VS Code window.
4. In that new VS Code window, open any python file and literally type:
`api_key = "sk_test_abcdefghijklmnopqrstuvwxyz"`
5. **Watch the magic:** A red squiggly line will instantly underline your text as you type it! Hover over it to show the judges the Zenith security popup!
   > *Point out to the judges*: "Zenith operates silently in the background via a FastAPI server, preventing developers from ever saving or committing a secret."

---

## 🏁 Outro
Wrap up the pitch by highlighting Zenith's biggest achievements:
1. **100% Privacy:** The code never leaves the developer's laptop. ML generation handles everything on Apple's Native Silicon.
2. **Zero Distractions:** Complete mitigation of False Positives.
3. **OS-Agnostic:** Built-in hardware routers mean it deploys on Windows, Linux, and Macs effortlessly.
