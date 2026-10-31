# ローカル開発状況 — 2026-11-01

## 実装した基盤

- sauna-api: Hummingbird実HTTPサーバ、OpenAPI生成契約、PostgresNIOローカル接続pool/診断、Apple container build/runとPostgreSQL18。
- sauna-web: 指定Bun/Svelte5スタック、Vintage/Pumpkin切替、非PII人数preview、生成OpenAPI型。
- sauna-admin-web: 同スタックのreadonly shell。認証・管理操作は未実装。
- .github / sauna-docs: Apple container・Web stackのADRとエージェント規則。

今回の変更はcodex/*ローカルブランチに保存し、push・新規PR・GitHub Actions・本番deployは実施していない。以前完了したGitHub基盤と今回のローカル検証は区別する。

## アクセス

- API: http://127.0.0.1:8080/health と /version
- 利用者Web: http://127.0.0.1:5173
- 管理者Web: http://127.0.0.1:5174
- DB: 127.0.0.1:55432、sauna_local / sauna_app（ローカル専用）

起動中processを終了した後の再起動手順は各repoのdocs/LOCAL_DEVELOPMENT.mdを参照する。Webのpreviewは予約・決済の完了を意味しない。

## 検証

APIはhost Swift25tests（実DB4件を含む）、Python16testsとOpenAPI4examples、Apple containerのLinux release build/testを実施。Linuxはsecretを渡さずDB4件をskipし21件成功。実HTTP、SIGTERM、DB停止/再起動、timeout/cancelと回復も確認した。

両Webはfrozen install、型検査、lint、unit19件ずつ、production build、Playwright6件ずつ、実API smokeを成功。利用者フォームの競合修正後は追加60ケースも成功した。独立Review Agentが再実行し、Security Review AgentがDBのsecret/権限/所有資源保護を確認した。各repoのdocs/LOCAL_VALIDATION.mdに詳細を記録する。

DB passwordはユーザーが明示許可したローカル専用値のみ生成し、Git除外の私有ファイルに保存。値は記録しない。他のAPIキー・秘密鍵は要求も生成もしていない。

## ライブラリ方針と次の作業

公式のHummingbird/PostgresNIO/Swift OpenAPI、SvelteKitと指定Web libraryを利用。現時点でforkが必要な上流不具合は見つかっていない。必要になったら再現テスト、最小fork差分、固定revision、上流PRの順に追跡する。

次はIssue/ADRの依存関係に従い、業務schemaとAtlas migration、施設境界のDB制約・統合テストへ進む。Passkey、予約競合、Stripe、Workspaceは未実装。外部credentialが必要になった時点で確認する。Safari実機/iOS、リモートCI、本番環境は今回未検証。
