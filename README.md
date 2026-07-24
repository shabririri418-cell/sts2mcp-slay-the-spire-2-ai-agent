# STS2MCP Slay the Spire 2 AI Agent

A single-purpose Codex skill for controlling, troubleshooting, and narrating
Slay the Spire 2 through [STS2MCP](https://github.com/Gennadiyev/STS2MCP).

## Capabilities

- Control single-player and multiplayer runs through the STS2MCP REST API or MCP server.
- Make version-aware combat, deck-building, routing, shop, event, and rest-site decisions.
- Use checkpoint-safe save/load recovery for pivotal branches and compatibility failures.
- Verify completed runs from run history instead of inferring victory from the final screen.
- Query a bundled, offline `zh-CN` WanWiki snapshot for cards, relics, potions,
  statuses, characters, acts, monsters, events, and glossary aliases without
  accessing the website during gameplay.
- Provide optional Chinese Tower-P commentary and license-gated local Mambo narration.

## Install

Install only this skill with the Skills CLI:

```bash
npx skills add shabririri418-cell/sts2mcp-slay-the-spire-2-ai-agent --skill sts2mcp-slay-the-spire-2-ai-agent
```

Or copy
`skills/sts2mcp-slay-the-spire-2-ai-agent`
into your Codex skills directory.

The STS2MCP game mod is installed separately. Follow the installation section in
[SKILL.md](skills/sts2mcp-slay-the-spire-2-ai-agent/SKILL.md).

## Repository layout

```text
skills/sts2mcp-slay-the-spire-2-ai-agent/
├── SKILL.md
├── agents/
├── references/
├── scripts/
├── tests/
└── .gitignore
```

The repository intentionally contains no unrelated skills and no workflow that
automatically generates new skills.

The WanWiki snapshot is reference-only, contains structured game knowledge
rather than raw pages or images, and has no runtime network updater. Current
coverage and provenance are recorded in
[`wanwiki-offline-knowledge.md`](skills/sts2mcp-slay-the-spire-2-ai-agent/references/wanwiki-offline-knowledge.md).

## Upstream

- Game mod and server: [Gennadiyev/STS2MCP](https://github.com/Gennadiyev/STS2MCP)
- Original skill collection: [Aradotso/mcp-skills](https://github.com/Aradotso/mcp-skills)
