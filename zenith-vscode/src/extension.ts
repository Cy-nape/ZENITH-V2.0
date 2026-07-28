import * as vscode from 'vscode';
import axios from 'axios';

const diagnosticCollection = vscode.languages.createDiagnosticCollection('zenith');

// A beautiful, highly visible inline badge and background highlight
const secretDecorationType = vscode.window.createTextEditorDecorationType({
    backgroundColor: 'rgba(220, 38, 38, 0.25)',     // Red tinted background
    border: '1px solid rgba(220, 38, 38, 0.5)',
    borderRadius: '4px',
    color: '#ffb3b3',
    fontWeight: 'bold',
    after: {
        contentText: ' 🛡️ ZENITH AI: BLOCKING LIVE SECRET ',
        color: '#ffffff',
        backgroundColor: '#dc2626',                 // Solid bright red badge
        fontWeight: '900',
        margin: '0 0 0 15px',
        textDecoration: 'none; border-radius: 4px; padding: 2px 8px; font-size: 11px; box-shadow: 0 0 8px #dc2626;' // Glow effect!
    }
});

// A subtle decoration for AI-verified mock/test secrets
const ignoredDecorationType = vscode.window.createTextEditorDecorationType({
    textDecoration: 'underline dotted rgba(100, 149, 237, 0.8)', // Subtle cornflower blue underline
    after: {
        contentText: ' ✓ verified mock ',
        color: 'rgba(100, 149, 237, 0.8)',
        margin: '0 0 0 15px',
        textDecoration: 'none; font-size: 10px; font-style: italic;'
    }
});

const debounceTimers = new Map<string, NodeJS.Timeout>();

async function scanDocument(doc: vscode.TextDocument) {
    if (doc.uri.scheme !== 'file' && doc.uri.scheme !== 'untitled') {
        return;
    }
    
    // Capture the document version before async request
    const reqVersion = doc.version;
    
    // Find the active editor for this document to apply decorations
    const editor = vscode.window.visibleTextEditors.find(e => e.document === doc);
    if (!editor) return;

    try {
        const response = await axios.post('http://127.0.0.1:8765/scan', {
            content: doc.getText(),
            filename: doc.fileName
        });

        // Discard stale responses if document has been edited since request
        if (doc.version !== reqVersion) {
            return;
        }

        const liveDecorations: vscode.DecorationOptions[] = [];
        const ignoredDecorations: vscode.DecorationOptions[] = [];
        
        for (const finding of response.data.findings) {
            const line = Math.max(0, finding.line - 1);
            const lineText = doc.lineAt(line).text;
            const range = new vscode.Range(line, 0, line, lineText.length);
            
            const isMock = finding.is_live === false || (finding.severity && finding.severity.startsWith("IGNORED"));
            
            // Build rich markdown hover pop-up
            const hoverMessage = new vscode.MarkdownString();
            hoverMessage.isTrusted = true;
            if (isMock) {
                hoverMessage.appendMarkdown(`### ✅ Zenith AI: Verified Mock\n\n`);
            } else {
                hoverMessage.appendMarkdown(`### 🚨 Zenith Security Violation\n\n`);
            }
            hoverMessage.appendMarkdown(`**Type:** ${finding.type}\n\n`);
            hoverMessage.appendMarkdown(`**Reason:** ${finding.reason}\n\n`);
            hoverMessage.appendMarkdown(`**Confidence:** ${finding.confidence ?? 'N/A'}\n\n`);
            hoverMessage.appendMarkdown(`---\n*Scanned in ${response.data.scan_time_ms}ms via ${response.data.engine}*`);

            if (isMock) {
                ignoredDecorations.push({ range: range, hoverMessage: hoverMessage });
            } else {
                liveDecorations.push({ range: range, hoverMessage: hoverMessage });
            }
        }
        
        // Apply both decoration arrays explicitly (clearing them if empty)
        editor.setDecorations(secretDecorationType, liveDecorations);
        editor.setDecorations(ignoredDecorationType, ignoredDecorations);
        
        // Clear status bar message if the request was successful
        vscode.window.setStatusBarMessage('');

    } catch (e) {
        console.error("Zenith Scan Error. Check if Python backend is running on port 8765.", e);
        vscode.window.setStatusBarMessage('Zenith: backend unreachable', 5000);
    }
}

function onDidChangeDebounced(doc: vscode.TextDocument) {
    const key = doc.uri.toString();
    const existingTimer = debounceTimers.get(key);
    if (existingTimer) {
        clearTimeout(existingTimer);
    }
    const timer = setTimeout(() => {
        debounceTimers.delete(key);
        scanDocument(doc);
    }, 600);
    debounceTimers.set(key, timer);
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Zenith extension is now active!');

    // Scan documents on save immediately and change with debounce
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(scanDocument),
        vscode.workspace.onDidChangeTextDocument(e => onDidChangeDebounced(e.document))
    );
    
    // Initial scan of active editors
    for (const editor of vscode.window.visibleTextEditors) {
        scanDocument(editor.document);
    }
}

export function deactivate() {
    for (const timer of debounceTimers.values()) {
        clearTimeout(timer);
    }
    debounceTimers.clear();
}

