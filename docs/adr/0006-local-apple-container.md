# ADR-0006: ローカル開発にApple containerを使う

Status: Accepted / 2026-11-01

## Context
ユーザーはローカルで可能な範囲まで進めること、Dockerを使わずApple containerを使うこと、APIキーや秘密鍵などが必要なら停止して確認することを明示した。

## Decision
ローカルのOCI build/runとPostgreSQL18の検証にはApple containerを使用する。Docker Engine/Desktop/CLI/Composeは使用しない。既存のCI設定変更やGCPへのデプロイはこのローカル作業に含めない。公式OCI imageの取得はDocker Engineの利用とは分離する。

実装はcodex/*ローカルブランチで行い、独立Review Agentを並行起動し、実ビルド・テスト・実HTTP/DB検証を記録する。リポジトリ外の共有container資源を削除せず、名前をsaunaで限定する。ホストの公開ポートは127.0.0.1に限定する。

APIキー・秘密鍵・DBパスワード等の必要性が発生した時点で依存作業を停止し、ユーザーに安全な設定手順を示して確認する。無断生成、既存secret探索、trust認証による迂回は行わない。必要になる前のローカルAPI構築や接続コードの準備は進められる。

## Validation
Apple container1.5.0の既存導入と稼働開始を確認。API HTTP/コンテナbuild/runとPostgreSQLの検証結果は各repoのローカル記録に追記する。

## References
- https://github.com/apple/container/tree/1.5.0
- https://github.com/apple/container/blob/1.5.0/docs/networking.md

## 承認済みの限定例外

このセッションでは、ユーザーがローカル開発用DB passwordの生成と私有ファイル保存を明示承認した。admin/app専用credentialを生成し、Git除外・directory0700/file0600で保存した。別用途のAPIキー・秘密鍵や外部サービス権限の承認には拡張しない。
