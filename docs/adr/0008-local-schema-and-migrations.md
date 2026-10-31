# ADR-0008: 施設参照整合性とforward-only migration

Status: Accepted / 2026-11-01

## Context

API Issue7のローカルPostgresNIO接続基盤に続き、Issue8のschema/migrationとIssue9のDB境界を実装する。初期1施設でもtenant keyを省略しない。API認証・施設別認可はまだ実装されていない。

## Decision

sauna-apiのdb/schema.sqlを正本とし、Atlas Community1.3.0でversioned SQLとatlas.sumを生成する。過去migrationの改変をtrusted Git baseとのbyte比較で拒否する。失敗やdriftへの対応は新しいforward fixで行い、自動rollbackや永続DB/volumeのresetは行わない。

施設、global user identity、施設membership、商品、予約、予約明細の最小schemaを配置する。施設内entityは(facility_id,id)の複合主キーとし、明細→予約/商品の外部キーもfacility_idを含める。global identityを社員membershipと分離し、施設membershipなしの利用者も将来予約できるモデルとする。

通貨はISO形式の3大文字、金額はminor unitのbigint。価格と商品名は予約明細のsnapshotに保持する。数量と有限の利用時間、正の期間をCHECK/NOT NULLで制約する。商品通貨と予約通貨の整合や金額合計、施設time_zoneのIANA検証、在庫・決済状態遷移は後続の業務transactionで実装する。

migration ownerはadmin、appには業務table DMLとschema USAGEのみ与える。複合FKは施設をまたぐ参照を拒否するが、閲覧・操作の認可ではない。任意のclient facility IDや未認証のsession設定をtrusted contextと扱わない。業務HTTP API公開前に、認証済みsubject、membership、施設ロールからread/write認可を実装する。

ローカルAtlas処理にはApple containerの既存PostgreSQL18を用いる。永続sauna_localと専用dev/replay DBを区別し、scratchは固定名/owner/DB commentを照合する。資格情報は承認済みlocal DB passwordだけをprivate一時configへ読み、argv/env/logへ出さない。

## Alternatives

単一idとfacility_idを独立FKで扱う案は、明細に他施設商品を混在できるため採用しない。共有app roleへowner権限を与える案も採用しない。RLSは認証済contextの設計・pool再利用時の安全性が未整備のため、この段階で認可完成の根拠にはしない。

Atlas Proのlint/managed driftには依存せず、CE schema diff、実replay、pglast ASTの保守的DDL guardを使用する。これは全migrationのlock/データ移行安全性を自動保証しない。非許可DDLには個別の方針レビューが必要。

## Validation and consequences

空DBへapply/reapply、schema一致、実drift canaryと自動修復しないこと、21件の制約/権限拒否を実app接続で確認。atlas.sumを再生成した過去改変もGit baseline guardが拒否した。独立Review/Securityが再検証した。詳しい手順/検証はsauna-apiのdocs/LOCAL_MIGRATIONS.mdとLOCAL_VALIDATION.mdに残す。

今回の変更はlocal branch/commitのみ。Issue8のGitHub CI接続、Issue9の認証済tenant context/API認可は未完了であり、Issueを完了扱いにしない。

## References

- https://github.com/sauna-studio/sauna-api/issues/8
- https://github.com/sauna-studio/sauna-api/issues/9
- https://www.postgresql.org/docs/18/ddl-constraints.html
- https://www.postgresql.org/docs/18/ddl-priv.html
- https://atlasgo.io/community-edition
- https://pglast.readthedocs.io/en/latest/
