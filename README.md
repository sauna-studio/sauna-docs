# sauna-docs
Sauna Studio architecture, ADRs, and development documentation


## Scope

アーキテクチャ・ADR・GitHub Wiki索引・依存関係を持つ横断バックログ。

## Architecture

.githubを共通規則の正本、各業務repoを実コードの正本として参照する。設計変更は背景・決定・代替案・影響をADRへ記録する。

## Verification

Markdownリンク・ADR整合性・backlogのキーと依存関係を検証する。Wiki反映前にGitHub側の実際の内容を確認する。

初期PRは開発基盤のみを追加します。CIはRepository policy検査を実行し、業務機能の実装や動作検証はまだ含みません。

[AGENTS.md](AGENTS.md) と [CONTRIBUTING.md](CONTRIBUTING.md) に従い、Issueの依存関係を満たしてから独立Review Agentを並行起動して実装します。共通規則適用元: [sauna-studio/.github@075c6695309d](https://github.com/sauna-studio/.github/tree/075c6695309d28baad2dc1391d7d3821b81142cc)。

設計文書: [Architecture ADR](docs/adr/0001-architecture.md) / [Wiki source](docs/wiki/Home.md) / [Backlog](docs/backlog.md)。
