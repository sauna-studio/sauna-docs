# ADR-0001: APIとPostgreSQLを業務データの正本にする

Status: Accepted / 2026-11-01

## Context
川沿いの小規模サウナ1施設から開始し複数施設に拡張する。貸切・共用サウナ、日帰り・宿泊テント、複数商品の同時予約、決済、チャット、設備・在庫・シフトを扱う。

## Decision
Swift 6 / Hummingbird API と PostgreSQL 18を正本とし、PostgresNIOで接続、schema.sqlを正本としAtlasのforward-only migrationsでスキーマを管理する。OpenAPIを契約としてSwift OpenAPI Generatorで生成し、SwiftUI (iOS/iPadOS 27.2以上) と SvelteKit/TypeScript の利用者・管理者クライアントを分離する。Google Cloud Run / Cloud SQLを予定するが本番デプロイや課金リソース作成は承認後とする。

施設境界には全業務エンティティのfacility_idと施設所属権限を用いる。クライアントの施設IDを信用せずAPIで認可する。共有ユーザーidentityと施設ごとのmembershipを分離し、施設を跨ぐ読み書きの否定テストを必須とする。

複数商品は1つの予約集約と明細で表し、在庫の一時確保・期限・競合制御をPostgreSQLトランザクションで原子的に実施する。共用サウナは人数、貸切/テントは時間区間の排他として容量を管理。河川増水・天候閉鎖は販売停止と影響予約の特定、監査付き取消・返金・通知に接続する。外部決済とDBは分散トランザクションにせず、状態機械・冪等キー・署名検証済webhook・outbox/reconciliationで整合を回復する。金額は通貨と最小単位の整数で保持する。

OpenTelemetryではtrace/log/metricの関連付けを行う。氏名、連絡先、チャット本文、Passkey challenge、Stripe payload、tokensを記録しない。予約IDなども必要最小限の属性とする。

## Consequences
API以外から業務DBを直接更新しない。Chat/Calendarは通知や投影であり予約の確定を担わない。競合・施設越境・決済再送/逆順・期限切れテストを実DBとStripe hosted Checkoutの期限仕様を確認し、Stripe test modeで検証するまで本番利用不可。

## References
- https://github.com/zunda-pixel/blindlog-api (構造参考。独自fork/branch依存を無検証で転用しない)
- https://github.com/hummingbird-project/hummingbird
- https://github.com/vapor/postgres-nio
- https://atlasgo.io/docs
