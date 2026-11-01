# ADR-0022: 既存DBから分離したAtlas migration CI

Status: Proposed / 2026-11-01

## Context

[API Issue8](https://github.com/sauna-studio/sauna-api/issues/8)は、空のPostgreSQL 18へのmigration適用と再適用、schema.sqlとの一致、drift・破壊的SQL・過去migration改変のCI検出を求める。既存のローカル検証で使ったsauna_atlas_replayは現在の開発APIも使用している。そのschemaをresetする旧helperをCI検証の再現に流用しない。

秘密情報が必要になった場合は確認するというユーザー指示に従い、今回は新しいpassword・外部API keyを必要としない方式を選ぶ。認証を無効化するtrust接続は使わない。

## Decision

新しい使い捨てPostgreSQL clusterでだけ検証する。ローカルはApple container、GitHub Actionsは既存Swift CIと同様のjob containerを使い、公式PostgreSQL 18 imageをdigest固定する。新しいDocker CLIのローカル導入は行わない。

ローカルcontainerへ渡すのは、Git追跡対象のschema.sql、migration、SQL test、検証shellとdigest照合済みAtlasの明示的な入力だけとする。repository全体、.git、.local、password file、既存volumeはmountしない。ローカルは新規の所有label付きcontainerをnetwork none・host公開portなしで起動する。CIのjob containerはGitHubのworkspace/networkを持つため、ローカルと同じnetwork遮断を保証するとは記録しない。

PostgreSQLは非rootのOS postgres userで起動する。listen_addressesを空にしてTCPを受け付けず、host認証はreject、所有者限定0700のUnix socket directoryとpeer認証を使う。pg_identはOS postgresから検証用DBのsauna_admin/sauna_appへの対応を明示する。これはkernelのOS identityを確認するローカル認証であり、任意userを受け入れるtrust認証ではない。実app-role接続でsession_user/current_userを確認し、adminのSET ROLEを代用にしない。

Atlas Community 1.3.0を公式versioned URLから取得し、platformごとの固定SHA256を実行前に照合する。Atlas Cloud tokenやPro機能は使わない。既存のmacOS用Atlasや既存DBの設定は変更しない。

## Trusted history

PRはeventのbase SHA、通常pushはbefore SHAを比較元にする。新規branchのzero-before時はfetch済みのorigin/mainを使い、手動実行はbase SHAを必須入力にする。完全SHA・commitの実在・対象HEADの祖先であること・過去migrationの存在を検証し、欠落時にHEAD自身へ黙って切り替えない。

比較元commitの既存guard/helperを隔離directoryへ展開し、candidateのSQLをそのguardで検査する。過去SQLのbyte比較とpglastの保守的なDDL許可規則を使い、atlas.sumの再生成だけで履歴改変を認めない。PR側のguard更新が既存規則を緩めることも避ける。

Workflow自体もPRで変更可能なため、この仕組みを悪意あるPRによるCI改変全般の防止策とは扱わない。CODEOWNERS、branch ruleset、最小permissions、独立レビュー、最新HEADのCodexレビューを引き続き必要とする。

## Verification and failure handling

新規cluster内にreplay/dev DBを用意し、checksum検証、空からのapply、二度目applyの履歴不変、schema.sqlとのdiffなしを確認する。実drift列を追加してdrift検査の失敗と列の残存を確認し、harness自身がcanaryを明示除去して一致を再確認する。実app-roleのSQL制約・施設越境・権限分離testも実行する。

隔離copyで過去SQLを書き換え、実Atlasによるhash更新とvalidate成功の後もtrusted byte guardが拒否することを検証する。破壊的SQLの拒否canaryも実行する。テストの存在、ローカルでの実行、GitHub CI成功は別々に記録する。

失敗時に既存DBへdown/resetや自動修復を行わない。新規clusterの終了と所有containerのcleanupだけを行う。永続環境では適用履歴とschemaを確認し、backup・復旧方針を決めた上でforward fixを追加・レビュー・再検証する。破壊的変更が必要な場合は保守的guardの制約を黙って迂回せず、別途policy変更をレビューする。

このCIはmigration/SQL検証であり、Swiftの実DBテストや本番Cloud SQL・backup復元・Workspace所属認可の完了を代替しない。新しいcheckは実mainで成功した後に、既存required checksを保持して必須化する。

## References

- [PostgreSQL peer authentication](https://www.postgresql.org/docs/18/auth-peer.html)
- [PostgreSQL initdb](https://www.postgresql.org/docs/18/app-initdb.html)
- [PostgreSQL connection settings](https://www.postgresql.org/docs/18/runtime-config-connection.html)
- [Atlas connection URLs](https://atlasgo.io/concepts/url)
- [Atlas Community](https://atlasgo.io/community-edition)
- [GitHub job containers](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/run-jobs-in-a-container)
