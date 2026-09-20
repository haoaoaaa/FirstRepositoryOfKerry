// Inspect the local VS Code install + user extensions/settings to find out why
// running a .c file complains about node.js.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const out = [];
const log = (...a) => out.push(a.join(' '));

function safe(label, fn) {
  try { log(label + ': ' + JSON.stringify(fn())); }
  catch (e) { log(label + ': <error> ' + e.message); }
}

safe('vscode exe', () => fs.existsSync('C:\\Program Files\\Microsoft VS Code\\Code.exe'));
safe('user extensions dir exists', () => fs.existsSync(path.join(os.homedir(), '.vscode', 'extensions')));
safe('user settings.json exists', () => fs.existsSync(path.join(os.homedir(), 'AppData', 'Roaming', 'Code', 'User', 'settings.json')));

// list extensions
safe('extensions dir', () => {
  const dir = path.join(os.homedir(), '.vscode', 'extensions');
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter(n => !n.startsWith('.'));
});

// dump settings.json
safe('user settings.json', () => {
  const p = path.join(os.homedir(), 'AppData', 'Roaming', 'Code', 'User', 'settings.json');
  if (!fs.existsSync(p)) return null;
  return fs.readFileSync(p, 'utf8');
});

// globalStorage: try to find code-runner config via workspace storage (avoid huge walk)
safe('Code User dir listing', () => {
  const p = path.join(os.homedir(), 'AppData', 'Roaming', 'Code', 'User');
  return fs.existsSync(p) ? fs.readdirSync(p) : [];
});

// what tasks.json exists in the workspace
for (const f of ['.vscode/settings.json', '.vscode/tasks.json', '.vscode/launch.json', '.vscode/c_cpp_properties.json']) {
  safe('workspace ' + f, () => fs.existsSync(f) ? fs.readFileSync(f, 'utf8') : null);
}

// learning dir contents
safe('learning/step0_hello contents', () => fs.readdirSync('learning/step0_hello'));

console.log(out.join('\n\n'));
