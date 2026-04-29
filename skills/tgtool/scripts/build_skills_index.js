#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '../../..');
const skillsRoot = path.join(repoRoot, 'skills');
const outputPath = path.join(repoRoot, 'skills', 'tgtool', 'skills-index.json');

function readFileSafe(p) {
  try {
    return fs.readFileSync(p, 'utf8');
  } catch {
    return null;
  }
}

function extractFrontmatter(content) {
  if (!content || !content.startsWith('---\n')) return {};
  const end = content.indexOf('\n---\n', 4);
  if (end === -1) return {};
  const block = content.slice(4, end);
  const out = {};
  for (const line of block.split('\n')) {
    const m = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!m) continue;
    const key = m[1].trim();
    let value = m[2].trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    out[key] = value;
  }
  return out;
}

function deriveTags(skillDirName, description) {
  const tags = new Set();
  skillDirName.split(/[-_:]+/).filter(Boolean).forEach((t) => tags.add(t.toLowerCase()));
  if (description) {
    for (const t of ['aws', 'debug', 'plan', 'review', 'test', 'security', 'memory', 'orchestration', 'openai', 'github']) {
      if (description.toLowerCase().includes(t)) tags.add(t);
    }
  }
  return [...tags].sort();
}

const entries = fs.readdirSync(skillsRoot, { withFileTypes: true })
  .filter((d) => d.isDirectory())
  .map((d) => d.name)
  .filter((name) => !name.startsWith('.'))
  .sort();

const skills = [];
for (const dir of entries) {
  const skillMd = path.join(skillsRoot, dir, 'SKILL.md');
  const raw = readFileSafe(skillMd);
  if (!raw) continue;

  const frontmatter = extractFrontmatter(raw);
  const name = frontmatter.name || dir;
  const description = frontmatter.description || '';

  const triggers = [];
  if (description) {
    const lower = description.toLowerCase();
    if (lower.includes('use when')) triggers.push('description:use-when');
    if (lower.includes('must use')) triggers.push('description:must-use');
  }

  skills.push({
    skill_id: name,
    path: `skills/${dir}/SKILL.md`,
    summary: description,
    tags: deriveTags(dir, description),
    triggers,
  });
}

const payload = {
  schema_version: '1.0.0',
  generated_at: new Date().toISOString(),
  mode_default: 'lazy',
  fallback_mode: 'full',
  total_skills: skills.length,
  skills,
};

fs.writeFileSync(outputPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
console.log(`Wrote ${skills.length} skills -> ${outputPath}`);
