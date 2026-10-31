# ADR-0010: blindlog-api固定commitをAPI実装の参照にする

Status: Accepted / 2026-11-01

## Context

ユーザーはblindlog-apiのPackage.swift（commit82a13ed73fff44984e8954781d669cf8320883ea）をAPIの参照にするよう指定した。Saunaでは既にHummingbird/OpenAPI/PostgresNIOと独立identity/DB targetsを用いている。

## Decision

固定commitのPackage.swift/Sources/Package.resolvedを調査起点とする。薄いentry point、composition root、依存注入APIProtocol、操作別handler/Model/Middleware分離を採用方針とする。Saunaの独立moduleと生成contractを維持する。

Swift6.4の全6UpcomingFeature、非隔離default、strictMemorySafety、warnings-as-errorsを自前productiontargetsへ共通適用する。必要な公開型だけpublic importで明示し、認証subjectのconstructorはinternalのままとする。生成物手編集や無根拠なunsafe/unchecked Sendableで回避しない。

依存/forkは盲目的に複製せず、SaunaのIssue受入とlicense/互換性/上流差分を確認する。HummingbirdAuth/WebAuthn protocol注入、型付きSQL/DB integration、swift-otel、通貨型を今後の評価起点とする。forkの可変branchではなく参照lockfileのrevisionを起点に追跡する。詳細はsauna-api/docs/BLINDLOG_REFERENCE.mdを正本とする。

## Alternatives and consequences

単一App targetへ全て統合する案はidentity生成境界とテスト分離を失うため採用しない。メールOTPログイン、Cloudflare前提、Valkey challenge正本はSaunaのPasskey-only/Google Cloud/PostgreSQL方針に適用しない。

参考forkのWebAuthn public initializerはtest seam用途であり、Saunaの認証済subjectを無検証で作る根拠にしない。PostgreSQL closure lifetime修正は同期adapter固有のためasync poolへunsafe処理をコピーしない。

厳格設定はコンパイラ検査を強めるが、全依存のmemory safetyを証明するものではない。build/test/境界検査と独立レビューを継続する。今回もlocal branch/commitのみ、remote push/PR/Actionsは行わない。

## References

- https://github.com/zunda-pixel/blindlog-api/blob/82a13ed73fff44984e8954781d669cf8320883ea/Package.swift
- https://github.com/zunda-pixel/blindlog-api/tree/82a13ed73fff44984e8954781d669cf8320883ea/Sources/App
