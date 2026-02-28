# mycodex-skills

Portable backup of my Codex user skills.

## Included layout

All skills are stored under `skills/`.

To import them on another machine:

```bash
mkdir -p ~/.codex/skills
cp -a skills/* ~/.codex/skills/
```

Then restart Codex so the new skills are picked up.

## Notes

- These are user-installed skills only.
- System skills under `~/.codex/skills/.system` are not mirrored here.
