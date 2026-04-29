#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) continue;
    const [k, vInline] = a.split('=');
    const key = k.slice(2);
    if (vInline !== undefined) {
      args[key] = vInline;
    } else {
      const next = argv[i + 1];
      if (!next || next.startsWith('--')) {
        args[key] = 'true';
      } else {
        args[key] = next;
        i++;
      }
    }
  }
  return args;
}

function readText(args) {
  let txt = '';
  if (args['input-file']) txt += fs.readFileSync(args['input-file'], 'utf8');
  if (args['input-text']) txt += args['input-text'];
  if (!txt && !process.stdin.isTTY) {
    try { txt += fs.readFileSync(0, 'utf8'); } catch (_) {}
  }
  return txt;
}

function estimateTokens(text) {
  let ascii = 0;
  let nonAscii = 0;
  for (const ch of text) {
    if (ch.charCodeAt(0) <= 127) ascii++;
    else nonAscii++;
  }
  const weightedChars = ascii + nonAscii * 1.7;
  return Math.ceil(weightedChars / 4);
}

function loadState(stateFile) {
  if (!fs.existsSync(stateFile)) return { total_estimated_tokens: 0, turns: 0, updated_at: null };
  try {
    return JSON.parse(fs.readFileSync(stateFile, 'utf8'));
  } catch {
    return { total_estimated_tokens: 0, turns: 0, updated_at: null };
  }
}

function saveState(stateFile, state) {
  fs.mkdirSync(path.dirname(stateFile), { recursive: true });
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
}

function level(pct) {
  if (pct > 92) return 'critical';
  if (pct > 85) return 'preview';
  if (pct > 70) return 'warn';
  return 'ok';
}

function recommendation(lv) {
  if (lv === 'critical') return 'Run final handoff (summary+compact) and start a new session now.';
  if (lv === 'preview') return 'Start Phase A preview handoff.';
  if (lv === 'warn') return 'Prepare handoff; avoid adding large context.';
  return 'Continue normally.';
}

(function main() {
  const args = parseArgs(process.argv);
  const cwd = process.cwd();
  const stateFile = args['state-file'] || path.join(cwd, '.tgtool', 'context_guard_state.json');
  const contextLimit = Number(args['context-limit'] || 200000);
  const fixedOverhead = Number(args['fixed-overhead'] || 2500);

  if (args.reset === 'true') {
    const resetState = { total_estimated_tokens: 0, turns: 0, updated_at: new Date().toISOString() };
    saveState(stateFile, resetState);
    console.log(JSON.stringify({ status: 'reset', state_file: stateFile }, null, 2));
    return;
  }

  const text = readText(args);
  const current = estimateTokens(text);

  const state = loadState(stateFile);
  state.total_estimated_tokens += current;
  state.turns += 1;
  state.updated_at = new Date().toISOString();
  saveState(stateFile, state);

  const total = state.total_estimated_tokens + fixedOverhead;
  const pct = (total / contextLimit) * 100;
  const lv = level(pct);

  const out = {
    status: 'ok',
    state_file: stateFile,
    turn_estimated_tokens: current,
    rolling_estimated_tokens: state.total_estimated_tokens,
    fixed_overhead_tokens: fixedOverhead,
    estimated_context_tokens: total,
    context_limit_tokens: contextLimit,
    estimated_context_pct: Number(pct.toFixed(2)),
    threshold_level: lv,
    recommendation: recommendation(lv)
  };

  console.log(JSON.stringify(out, null, 2));
})();
