# Changelog

All notable changes to the **BlendAI Swarm** project will be documented in this file.

## [1.7.0] - 2026-04-14
### Added
- **Shielded Context Architecture**: Multi-layer defense against Indirect Prompt Injection and Data Poisoning.
- **Stateless Scrubber**: High-speed regex engine for real-time redaction of malicious instruction overrides.
- **Instruction Isolation**: Uses strict `[UNTRUSTED_DATA]` delimiters to prevent data-to-instruction leakage.
- **MTime-Aware Caching**: Optimized Skill Library discovery with directory-modified timestamp caching.
- **Professional Logging**: Integrated centralized logging suite (`blendai_swarm.log`) for technical audits.

## [1.6.0] - 2026-04-13
### Added
- **Gold Master Certification**: Passed 18-suite unified QA audit with 100% success.
- **Security Auditor**: `CriticAgent` now explicitly blocks `os` and `subprocess` modules.
- **Evolutionary Versioning**: Non-destructive `_v2`, `_v3` skill saving system.

## [1.3.0] - 2026-04-13
### Added
- **Skill Library**: Discovery system for specialized `.py` scripts.
- **Autonomous Promotion**: Swarm can now suggest "promoting" its own code into new reusable skills.
- **Session Continuity**: Multi-turn persistent memory using local Markdown logs.

## [1.0.0] - 2026-04-13
### Added
- Initial release of the 4-agent Autonomous Swarm (Manager, Planner, Executor, Critic).
- Native Blender UI Sidebar integration.
