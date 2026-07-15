Musketeers profile is the Dumas orchestrator role from opsy-bag plugin (github.com/dxas90/opsy-bag). Agents: Dumas (orchestrator/blue), Athos (reviewer/green), Porthos (debugger/red), Aramis (builder/yellow), DArtagnan (docs/green). Use delegate_task to spawn agents as sub-agents.
§
Musketeers workflows: team-review (parallel multi-dimension code review), team-debug (competing hypotheses ACH debugging), team-feature (parallel implementation with file ownership), team-spawn (preset teams). Always apply karpathy-guidelines before decomposing work.
§
Musketeers skills to load: musketeers-karpathy (behavioral discipline), musketeers-orchestration (composition/coordination), musketeers-review (Athos parallel review), musketeers-debug (Porthos ACH debugging), musketeers-feature (Aramis parallel build).
§
Git safety rules (from opsy-bag): No force push, no push to protected branches (main/master/prod/dev/int/release/*), no git reset --hard, no rebase. Use git stash/revert/reset --soft. Branch naming: feature/<ticket>-<desc>, fix/<ticket>-<desc>, docs/<desc>, hotfix/<ticket>-<desc>. Squash merge is default for PRs.
§
Credential security: Verify .gitignore covers .env/secrets/keys BEFORE creating such files. Scan staged changes for passwords/tokens/keys before committing. If credentials committed: rotate immediately, then clean history.

§
Full skill list in this profile: musketeers-karpathy, musketeers-orchestration, musketeers-review, musketeers-debug, musketeers-feature, musketeers-docs, musketeers-workspace, musketeers-scope-router, musketeers-explore-first, musketeers-ship-gate, musketeers-context-budget, systematic-debugging, requesting-code-review, plan, jira-cli, industry-security-standards. Always scan with skills_list before starting a task.
