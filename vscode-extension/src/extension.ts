import * as path from 'path';
import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    const pythonPath = vscode.workspace
        .getConfiguration('fitplan')
        .get<string>('pythonPath', 'python3');

    const serverModule = context.asAbsolutePath(
        path.join('..', 'fitplan', 'lsp_server.py')
    );

    const serverOptions: ServerOptions = {
        command: pythonPath,
        args: [serverModule],
        transport: TransportKind.stdio
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'fitplan' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.fitplan')
        }
    };

    client = new LanguageClient(
        'fitplan',
        'FitPlan DSL',
        serverOptions,
        clientOptions
    );

    client.start();

    vscode.window.showInformationMessage('FitPlan DSL is ready!');
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}