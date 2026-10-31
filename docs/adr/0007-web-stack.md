# ADR-0007: Webスタックを統一する

Status: Accepted / 2026-11-01

## Decision
ユーザー指定に従い、sauna-web / sauna-admin-webを以下へ統一する。

| 領域 | 採用 |
| --- | --- |
| フレームワーク/UI | SvelteKit / Svelte 5 Runes |
| 言語 | TypeScript strict |
| 依存管理/ローカルruntime | Bun |
| Build | Vite (SvelteKit標準) |
| CSS | Tailwind CSS v4 |
| Component/Icon | shadcn-svelte / Lucide Svelte |
| Form/Validation | Superforms + Zod |
| API client | openapi-fetch (OpenAPI生成型) |
| Unit/E2E | Vitest / Playwright |
| Quality | ESLint + Prettier |

Bunのlockfileと使用versionを記録し、実check/lint/unit/production build/browser testを行う。SvelteKit・Svelte5と各libraryの現安定版互換性を公式情報で確認する。公式Bun adapterが対象で利用可能なら使用する。デプロイruntime/adapterはデプロイ先が決まった時点で再確認する。

認証/決済/施設認可の前提Issueが未完了の管理機能を仮実装で成功扱いにしない。APIは業務データの正本であり、OpenAPIから生成する型とAPI側認可を使う。初期フォーム検証は非PIIのローカルpreviewのみとし、未実装の予約・決済・ログインを実動と誤認させない。

## References
- https://svelte.dev/docs/kit/introduction
- https://svelte.dev/docs/svelte/what-are-runes
- https://bun.sh/docs/installation
- https://www.shadcn-svelte.com/docs/installation/sveltekit
- https://superforms.rocks/
- https://openapi-ts.dev/openapi-fetch/

## ローカル検証時の選定

Bun1.4.4、SvelteKit3.1.1、Svelte5.57.3と公式adapter-bun1.0.0を使用。TypeScriptはKitのpeer対応に合わせ6.0.3を固定し、peer外の7系は現時点で採用しない。shadcn CLIは公式生成ソースを使い、Bun実行は成功したがCLIのsupported-runtime警告も検証記録へ残す。バージョンは検証時のもので、更新時にpeer・公式対応を再確認する。
