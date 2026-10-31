# Sauna Studio backlog

提供されたSAUNA_STUDIO_CONTEXT.mdの計画IDとグループ意図を引継ぎ資料として採用。元の個別50件・T15件・W14件の原文題名は資料にないため、以下は要件から具体化したIssueであり原文の再現ではない。

## 構成

- MVP: `MVP-001`–`MVP-050` の50件。計画IDは B01–B08 / A01–A06 / R01–R08 / P01–P07 / O01–O06 / C01–C10 / Q01–Q05。
- GitHub基盤: `FOUND-001`–`FOUND-008` の8件、G01–G08。
- Chat/MCP: T01–T15の15件。Workspace: W01–W14の14件。既存 `INTEGRATION-001`–`007` を保持し、`008`–`029` を追加。
- 親Epic7件を含め合計94件。

安定キーとrepoは初稿から変更していない。正本は [backlog.json](backlog.json)。既存Issueをキーで照合し、planning_idと受け入れ条件・依存リンクを本文へ同期する。Sub-issuesとblocking dependenciesは本文リンクとは別にAPI上でも検証する。

## 元計画との対応と coverage gap

引継ぎ資料にあるのは件数・グループ意図・横断要件で、元個別Issueの題名・本文はない。各metadataの `planning_mapping` と `planning_note` に対応精度を残す。`group-intent` も原文一致の意味ではない。元の詳細が得られた場合はキーの重複作成をせず再照合する。

| 計画ID | 現在キー | 対応上の留意点 |
| --- | --- | --- |
| P05 | MVP-024 | Payments群への対応は支払状態の利用者表示に限定。元P05の個別意図は資料にないため原文一致は未確認。 |
| P06 | MVP-045 | Payments群への対応は決済/予約競合の統合検証。品質検証も含む横断Issueで元P06との一致は未確認。 |
| P07 | MVP-047 | Payments群への対応は決済監査を含む業務監査。元P07の個別意図は未確認。 |
| C10 | MVP-046 | Clients群への対応は退会・保持・削除の利用者フロー仕様。文書中心の横断Issueで元C10の実装意図は未確認。 |
| C09 | MVP-049 | Clients群への対応は全クライアントのアクセシビリティ検証。品質横断Issueで元C09との一致は未確認。 |

C09/C10とP05–P07は横断的な表示・検証・監査・プライバシー仕様への暫定割当であり、元計画に別の実装意図があった可能性が残る。代理予約・洪水/天候閉鎖・account recoveryは既存Issueの受け入れ範囲へ追加し、未実装を完了扱いにしない。

## 最初の実装

`FOUND-001`完了後に `MVP-001`（B01、OpenAPI health/version契約）を開始し、次の `MVP-002` でHummingbirdを実行可能にする。共通ポリシーの提供と各repoへの明示配置は別の受け入れ条件。

## 決定の反映

- schema.sqlを正本とし、Atlas migrationはforward-only。
- Passkeyのみのログイン、複数credentialと安全なrecovery、active Workspace/Group所属と退職失効。
- 予約と決済は独立した状態機械。原子作成はpending_paymentとし、支払済confirmedは検証済決済処理のみ。
- 洪水・天候閉鎖で新規販売を止め、影響予約・取消/返金/通知を監査可能に扱う。
- Chat/MCP初期機能はread-only。敏感操作はaction requestとadmin UIのfresh Passkey承認。
- MCP Swift SDK / Streamable HTTP / OAuth 2.1互換認可。未検証role/tenantは権限に使わない。
- Calendar初期同期は一方向。Cloud Swift SDKの対応とWorkspace typed REST adapterを区別する。

2026-11-01の公式[Stripe Create Session](https://docs.stripe.com/api/checkout/sessions/create?query=expires_at)確認では、hosted Checkoutのexpires_atは作成後30分〜24時間、既定24時間。[明示expire](https://docs.stripe.com/api/checkout/sessions/expire)はopen Sessionに適用する。短い在庫holdを設定する場合はexpire・決済照合・遅延成功時の補償を一体で設計し、実装時に選定API版を再確認する。

## 依存順

同一グループでも依存先の受け入れ条件を満たすまでは完了扱いにしない。親Epicの包含と実装blockerは区別する。

1. **EPIC-001 / EPIC-001** `.github` — GitHub 開発基盤（依存: なし）
2. **EPIC-002 / EPIC-002** `sauna-api` — API・認証・施設境界（依存: なし）
3. **EPIC-003 / EPIC-003** `sauna-api` — 予約・在庫・決済（依存: なし）
4. **EPIC-004 / EPIC-004** `sauna-web` — 利用者・管理者クライアント（依存: なし）
5. **EPIC-005 / EPIC-005** `sauna-infrastructure` — 運用・品質・リリース（依存: なし）
6. **EPIC-006 / EPIC-006** `sauna-automation` — Google Workspace・Chat・MCP 連携（依存: なし）
7. **EPIC-007 / EPIC-007** `sauna-api` — スタッフ業務・チャット（依存: なし）
8. **FOUND-001 / G01** `.github` — Organization 共通開発基盤を整備する（依存: なし）
9. **FOUND-002 / G02** `.github` — 8 リポジトリを安全に初期化する（依存: FOUND-001）
10. **FOUND-003 / G03** `.github` — Organization Project と Issue グラフを構築する（依存: FOUND-001）
11. **FOUND-007 / G07** `.github` — MCP・Skills とローカルツールの実行可能性を監査する（依存: FOUND-001）
12. **MVP-001 / B01** `sauna-api` — OpenAPI の health・version 契約を定義する（依存: FOUND-001）
13. **FOUND-004 / G04** `.github` — Rulesets と Required Checks を設定する（依存: FOUND-002）
14. **FOUND-005 / G05** `.github` — 依存関係・コード・Secret のセキュリティ検査を整備する（依存: FOUND-002）
15. **FOUND-006 / G06** `sauna-docs` — ADR と GitHub Wiki の運用を開始する（依存: FOUND-002）
16. **FOUND-008 / G08** `.github` — 言語別 CI とリリース・Environment 規約を整備する（依存: FOUND-002）
17. **MVP-002 / B02** `sauna-api` — Hummingbird の実行可能な API 雛形を構築する（依存: MVP-001）
18. **INTEGRATION-001 / W01** `sauna-automation` — Google Workspace 認可と API 対応表を設計する（依存: FOUND-006）
19. **MVP-003 / B03** `sauna-api` — PostgreSQL 18 と PostgresNIO の基盤を構築する（依存: MVP-002）
20. **MVP-030 / B06** `sauna-web` — SvelteKit 利用者 Web の基盤を作成する（依存: FOUND-008, MVP-001）
21. **MVP-037 / B07** `sauna-app` — SwiftUI iOS・iPadOS 利用者アプリ基盤を作成する（依存: FOUND-008, MVP-001）
22. **MVP-004 / B04** `sauna-api` — Atlas によるマイグレーションを導入する（依存: MVP-003）
23. **INTEGRATION-029 / W14** `sauna-automation` — Google Cloud Swift SDK と Workspace REST adapter を区分する（依存: INTEGRATION-001）
24. **MVP-005 / B05** `sauna-api` — 施設境界と tenant context を強制する（依存: MVP-004）
25. **INTEGRATION-002 / W02** `sauna-automation` — Directory による社員所属確認を実装する（依存: INTEGRATION-001, MVP-005）
26. **MVP-006 / A01** `sauna-api` — Passkey challenge のライフサイクルを実装する（依存: MVP-005）
27. **MVP-012 / R01** `sauna-api` — サウナ・テントの商品カタログ API を実装する（依存: MVP-005）
28. **MVP-007 / A02** `sauna-api` — Passkey 登録を実装する（依存: MVP-006）
29. **MVP-013 / R02** `sauna-api` — リソース・在庫台帳を実装する（依存: MVP-012）
30. **MVP-008 / A03** `sauna-api` — Passkey ログインを実装する（依存: MVP-007）
31. **MVP-014 / R03** `sauna-api` — 価格・営業日・時間帯ルールを実装する（依存: MVP-013）
32. **MVP-009 / A04** `sauna-api` — セッション・ログアウト・Passkey 管理を実装する（依存: MVP-008）
33. **MVP-015 / R04** `sauna-api` — 空き状況検索 API を実装する（依存: MVP-014）
34. **INTEGRATION-003 / W03** `sauna-api` — Passkey 利用者と Workspace 社員 ID を紐付ける（依存: INTEGRATION-002, MVP-009）
35. **MVP-016 / R05** `sauna-api` — 複数商品カートと見積もりを実装する（依存: MVP-015, MVP-009）
36. **MVP-031 / C01** `sauna-web` — Web の Passkey 認証 UI を実装する（依存: MVP-030, MVP-009）
37. **MVP-032 / C02** `sauna-web` — 商品・空き状況検索画面を実装する（依存: MVP-030, MVP-015）
38. **MVP-038 / C06** `sauna-app` — Apple アプリの Passkey 認証を実装する（依存: MVP-037, MVP-009）
39. **MVP-010 / A05** `sauna-api` — Workspace 必須の社員プロビジョニングを実装する（依存: INTEGRATION-003）
40. **MVP-017 / R06** `sauna-api` — 期限付き在庫 hold と競合制御を実装する（依存: MVP-016）
41. **INTEGRATION-023 / W08** `sauna-automation` — Workspace OAuth token の安全な保管・更新・失効を実装する（依存: INTEGRATION-001, INTEGRATION-003）
42. **MVP-011 / A06** `sauna-api` — スタッフの施設別ロール・認可を実装する（依存: MVP-010）
43. **MVP-018 / R07** `sauna-api` — 複数商品予約の支払待ち集約を原子的に作成する（依存: MVP-017）
44. **INTEGRATION-006 / W05** `sauna-automation` — Groups・Drive の必要範囲を連携する（依存: INTEGRATION-003, MVP-011）
45. **MVP-019 / R08** `sauna-api` — hold 失効・在庫解放ジョブを実装する（依存: MVP-018）
46. **MVP-026 / O02** `sauna-api` — 管理者の商品・価格・営業設定 API を実装する（依存: MVP-014, MVP-011）
47. **MVP-027 / O03** `sauna-api` — 設備状態・メンテナンス枠を管理する（依存: MVP-017, MVP-011）
48. **MVP-028 / O04** `sauna-api` — スタッフシフト API を実装する（依存: MVP-011）
49. **MVP-020 / P01** `sauna-api` — Stripe Checkout と決済開始を実装する（依存: MVP-019）
50. **MVP-035 / C05** `sauna-admin-web` — 管理者 SvelteKit Web と予約・設備管理を実装する（依存: FOUND-008, MVP-026, MVP-027, MVP-031）
51. **INTEGRATION-021 / W06** `sauna-automation` — Workspace の stable ID・active・Group 所属を検証する（依存: INTEGRATION-002, INTEGRATION-006）
52. **INTEGRATION-026 / W11** `sauna-automation` — Drive・Docs の運用資料参照を最小権限で連携する（依存: INTEGRATION-006, INTEGRATION-023）
53. **MVP-021 / P02** `sauna-api` — Stripe webhook の検証と冪等処理を実装する（依存: MVP-020）
54. **INTEGRATION-022 / W07** `sauna-automation` — 所属再検証・退職時の権限とセッション失効を実装する（依存: INTEGRATION-003, INTEGRATION-021, MVP-011）
55. **MVP-022 / P03** `sauna-api` — 決済照合と例外回復を実装する（依存: MVP-021）
56. **MVP-033 / C03** `sauna-web` — 複数商品予約と Stripe 遷移 UI を実装する（依存: MVP-031, MVP-032, MVP-021）
57. **MVP-023 / P04** `sauna-api` — 予約取消・キャンセル料・返金を実装する（依存: MVP-022）
58. **MVP-024 / P05** `sauna-api` — 利用者の予約一覧・詳細 API を実装する（依存: MVP-023）
59. **MVP-025 / O01** `sauna-api` — 利用者・スタッフ間チャット API を実装する（依存: MVP-024, MVP-011）
60. **MVP-029 / O05** `sauna-api` — 業務イベント outbox と通知を実装する（依存: MVP-024, MVP-028）
61. **INTEGRATION-004 / T01** `sauna-automation` — Google Chat Sauna Bot を実装する（依存: INTEGRATION-003, MVP-024, MVP-029）
62. **INTEGRATION-005 / W04** `sauna-automation` — Calendar に予約・シフトの派生ビューを同期する（依存: INTEGRATION-003, MVP-028, MVP-029）
63. **MVP-034 / C04** `sauna-web` — 予約管理とチャット画面を実装する（依存: MVP-033, MVP-025）
64. **MVP-036 / O06** `sauna-admin-web` — シフト・社員・チャット管理画面を実装する（依存: MVP-035, MVP-028, MVP-025）
65. **MVP-039 / C07** `sauna-app` — 利用者アプリの予約・決済・チャットを実装する（依存: MVP-038, MVP-025, MVP-033）
66. **MVP-041 / Q01** `sauna-infrastructure` — OpenTelemetry の trace・metric・log を整備する（依存: MVP-002, MVP-029）
67. **MVP-046 / C10** `sauna-docs` — 個人情報の保持・削除・利用規約を設計する（依存: FOUND-006, MVP-025）
68. **INTEGRATION-027 / W12** `sauna-automation` — Gmail による組織向け業務通知の境界を定義する（依存: INTEGRATION-001, INTEGRATION-023, MVP-029）
69. **MVP-040 / C08** `sauna-admin-app` — SwiftUI 管理者アプリを実装する（依存: MVP-037, MVP-038, MVP-036）
70. **MVP-042 / B08** `sauna-api` — API コンテナと PostgreSQL 18 開発環境を作成する（依存: MVP-003, MVP-041）
71. **MVP-047 / P07** `sauna-api` — 業務監査ログを実装する（依存: MVP-023, MVP-028, MVP-046）
72. **INTEGRATION-009 / T04** `sauna-automation` — Google Chat イベントの送信元検証と重複排除を実装する（依存: INTEGRATION-004）
73. **INTEGRATION-010 / T05** `sauna-automation` — Bot の施設・空き状況・予約 read-only 照会を実装する（依存: INTEGRATION-004, MVP-015, MVP-024）
74. **INTEGRATION-011 / T06** `sauna-automation` — 予約・決済の業務通知を Google Chat に配信する（依存: INTEGRATION-004, MVP-029）
75. **INTEGRATION-012 / T07** `sauna-automation` — シフト変更と業務予定を Google Chat へ通知する（依存: INTEGRATION-004, MVP-028, MVP-029）
76. **INTEGRATION-013 / T08** `sauna-automation` — サポート件数照会と将来の Chat bridge 境界を定義する（依存: INTEGRATION-004, MVP-025）
77. **INTEGRATION-014 / T09** `sauna-automation` — 洪水・天候閉鎖と業務障害を Google Chat へ通知する（依存: INTEGRATION-004, MVP-027, MVP-029）
78. **INTEGRATION-024 / W09** `sauna-automation` — Calendar の予約・シフト・設備・閉鎖マッピングを実装する（依存: INTEGRATION-005, MVP-027）
79. **INTEGRATION-007 / T02** `sauna-automation` — sauna-mcp の認可付き業務ツールを実装する（依存: INTEGRATION-003, MVP-024, MVP-047）
80. **MVP-043 / Q02** `sauna-infrastructure` — Cloud Run・Cloud SQL の Terraform を設計・検証する（依存: FOUND-008, MVP-042）
81. **MVP-045 / P06** `sauna-api` — 予約・決済・認証の統合・競合テストを整備する（依存: MVP-023, MVP-009, MVP-042）
82. **MVP-049 / C09** `sauna-web` — アクセシビリティと最新安定ブラウザ互換性を検証する（依存: MVP-034, MVP-036, MVP-039, MVP-040）
83. **INTEGRATION-015 / T10** `sauna-automation` — 敏感操作の action request と fresh Passkey 承認を実装する（依存: MVP-009, MVP-011, MVP-047, INTEGRATION-004）
84. **INTEGRATION-025 / W10** `sauna-automation` — Calendar 同期の再試行・drift・再構築を検証する（依存: INTEGRATION-024）
85. **MVP-044 / Q03** `sauna-infrastructure` — staging 用 CI/CD と Environment を定義する（依存: MVP-043）
86. **INTEGRATION-008 / T03** `sauna-automation` — Google Chat Bot・Workspace Sync・MCP を別プロセスとして分離する（依存: INTEGRATION-004, INTEGRATION-007）
87. **INTEGRATION-016 / T11** `sauna-automation` — sauna-mcp の OAuth 2.1互換認可を検証する（依存: INTEGRATION-007）
88. **INTEGRATION-017 / T12** `sauna-automation` — read-only MCP tools の schema と結果範囲を整備する（依存: INTEGRATION-007, MVP-028, MVP-025）
89. **INTEGRATION-019 / T14** `sauna-automation` — 自動化処理の rate limit・retry・可観測性を整備する（依存: MVP-041, INTEGRATION-004, INTEGRATION-007）
90. **INTEGRATION-028 / W13** `sauna-automation` — Workspace adapter の契約・障害・所属検証テストを整備する（依存: INTEGRATION-022, INTEGRATION-025, INTEGRATION-026, INTEGRATION-027）
91. **MVP-048 / Q04** `sauna-docs` — 障害対応・backup・復旧手順を整備する（依存: MVP-044, MVP-047）
92. **INTEGRATION-018 / T13** `sauna-automation` — Bot・MCP の独立 Tool/Security Review を実施する（依存: INTEGRATION-007, INTEGRATION-016, INTEGRATION-017）
93. **INTEGRATION-020 / T15** `sauna-automation` — Bot・MCP の CI・非本番検証・運用手順を整備する（依存: INTEGRATION-018, INTEGRATION-019, INTEGRATION-008）
94. **MVP-050 / Q05** `sauna-docs` — MVP の受け入れ・リリース判定を実施する（依存: MVP-045, MVP-048, MVP-049, INTEGRATION-004, INTEGRATION-005, INTEGRATION-006, INTEGRATION-007, INTEGRATION-020, INTEGRATION-028, INTEGRATION-029）

## 実装・レビュー条件

すべての実装でCoding Agentと独立Review Agentを並行起動する。認証・決済・予約競合・個人情報・施設権限・Workspace所属・webhookではSecurity Review Agentも使用する。MCP契約・副作用は独立Tool Reviewでも確認する。実ビルド・テスト・利用可能なMCPによる検証結果と未検証範囲をPRに記録する。

バグは既存Issueを照合して重複を避け、回帰テストと再レビューを行う。重要な設計と継続的な指摘はADRと必要に応じたAGENTS.md更新へ反映する。GoogleChatAppとその個人Projectは対象外。本番deploy、有料リソース作成、広範な権限付与はこの計画によって承認されない。
