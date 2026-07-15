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

async function scanDocument(doc: vscode.TextDocument) {
    if (doc.uri.scheme !== 'file' && doc.uri.scheme !== 'untitled') {
        return;
    }
    
    // Find the active editor for this document to apply decorations
    const editor = vscode.window.visibleTextEditors.find(e => e.document === doc);
    if (!editor) return;

    try {
        const response = await axios.post('http://127.0.0.1:8765/scan', {
            content: doc.getText(),
            filename: doc.fileName
        });

        const decorations: vscode.DecorationOptions[] = [];
        
        for (const finding of response.data.findings) {
            const line = Math.max(0, finding.line - 1);
            const lineText = doc.lineAt(line).text;
            
            const range = new vscode.Range(line, 0, line, lineText.length);
            
            // Build rich markdown hover pop-up
            const hoverMessage = new vscode.MarkdownString();
            hoverMessage.isTrusted = true;
            hoverMessage.appendMarkdown(`### 🚨 Zenith Security Violation\n\n`);
            hoverMessage.appendMarkdown(`**Type:** ${finding.type}\n\n`);
            hoverMessage.appendMarkdown(`**Reason:** ${finding.reason}\n\n`);
            hoverMessage.appendMarkdown(`---\n*Scanned in ${response.data.scan_time_ms}ms via ${response.data.engine}*`);

            decorations.push({
                range: range,
                hoverMessage: hoverMessage
            });
        }
        
        // Apply our stunning custom decoration (removes the boring red squiggly)
        editor.setDecorations(secretDecorationType, decorations);
        
    } catch (e) {
        console.error("Zenith Scan Error. Check if Python backend is running on port 8765.", e);
    }
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Zenith extension is now active!');

    // Scan documents on save and change
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(scanDocument),
        vscode.workspace.onDidChangeTextDocument(e => scanDocument(e.document))
    );
    
    // Initial scan of active editors
    for (const editor of vscode.window.visibleTextEditors) {
        scanDocument(editor.document);
    }
}

export function deactivate() {}
