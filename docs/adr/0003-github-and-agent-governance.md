# ADR-0003: GitHub横断管理と独立並行レビュー

Status: Accepted / 2026-11-01

## Decision
Organization Projectを9リポジトリ横断の計画・進捗管理に使う。Issueのstable key、受け入れ条件、ネイティブ依存関係、Sub-issuesを併用する。共有会話の原文50件は取得できておらず、今回の50件は提示要件からの暫定再構成。照合後もstable keyを維持する。

共通規則は.githubで管理するがAGENTS/CODEOWNERS/CIは自動継承されないため全repoにコピーを明示配置する。共通workflowはレビュー済commit SHA参照で利用する。変更はcodex/* branchとPRで行う。新規空repoの最初のREADMEだけはGitHub repository auto-initializationを使用し、アプリ/基盤変更をmainに直接pushしない。

追加資料はprivate初期化を提案していたが、最新ユーザー指示「公開リポジトリで良いです。」を優先し9repoをpublicとする。FreeプランでのRulesets/Wiki等を実APIで確認して利用する。機密・個人情報・環境固有情報を公開repoに格納しない。既存repoは上書きせず差分をPRにする。

Coding Agent実行中に独立Review Agentを並行起動する。認証・決済・予約競合・個人情報・施設権限の実装時は独立Security Review Agentも起動する。AIレビューはビルド/実テスト/MCP検証の代用にしない。唯一のownerしかいない現時点ではrequired approving reviewsは0、PRと実際に成功したCIチェックをRulesetで必須にし、独立レビュー結果をPRに記録する。自己承認を要求して開発不能にしない。ルールの緩和やbypassを通常フローにしない。

Releasesはタグと成果物の検証後、Environmentsは本番接続なしで名前だけ用意する。Packagesは配布対象ができてからGHCR等を採用する。無料quotaを超えるActions/Packagesや本番GCPリソースは作成しない。

## References
- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file
- https://docs.github.com/en/rest/issues/issue-dependencies
- https://docs.github.com/en/rest/issues/sub-issues
- https://learn.chatgpt.com/docs/agent-configuration/subagents
