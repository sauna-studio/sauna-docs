# ADR-0021: ローカル施設HTTPの認証と認可の境界

Status: Proposed / 2026-11-01

## Context

[API Issue9](https://github.com/sauna-studio/sauna-api/issues/9)には、二施設の一覧・詳細・更新で施設越境を拒否する受け入れ条件がある。既存のFacilityStoreはmembership/roleとfacility/productを同じSQLで検査しているが、認証済みHTTPへの接続は未実装だった。[子Issue59](https://github.com/sauna-studio/sauna-api/issues/59)でローカルの接続と実PostgreSQL/HTTP検証を進める。

Passkeyログインは利用者のidentityを証明する。staff向けoriginでログインした事実だけでは、社員の所属や特定施設へのアクセス権限を証明しない。[Issue8](https://github.com/sauna-studio/sauna-api/issues/8)のAtlas migration CIも未完了であり、この部分実装で親Issueの依存関係を解消したとは扱わない。

## Decision

明示的なローカル認証opt-inとloopback bindの既存制約下で、staff向けoriginからの商品一覧・詳細・商品名更新を追加する。これはsynthetic membershipで施設境界を検証するための機能であり、Workspace確認済みの本番staff APIとして公開しない。利用者向けoriginの正当なセッションもstaff操作には使えない。

HTTPは既存SessionStoreでセッションを照合し、外部からVerifiedSubjectを組み立てるfactoryを追加しない。商品への各SQL statementでも、セッションのdigest・origin・有効期限・失効状態・有効credentialと、対象施設のactive membershipおよび操作に必要なroleを同時に検査する。クライアントのfacility IDは検索対象であり、認可の根拠ではない。一覧・詳細はowner/manager/staff、更新はowner/managerに限定する。

認証済みのidentityを先に取得しただけで、後続操作を無期限に認可しない。既存の期限付き・取消可能なDB接続leaseとtransactionを使い、セッション確認と業務操作のlifetimeを閉じる。取消はcommit前にも確認する。接続を閉じるだけのautocommit更新では、ロック待機の解除後に遅れて確定する可能性があるため、transactionでのrollbackと、ロック待機をdeadlineで取り消した場合のデータ不変を検証する。COMMIT送信後の通信断では確定結果が不明な場合があり、失敗応答が常に未更新を意味するとは扱わない。

READ COMMITTEDのstatement snapshotで、次のstatementより前にcommit済みの失効を拒否する。UPDATEの認可predicateは商品row lockの待機前に評価され得るため、既に開始したstatementの待機中に発生した失効・期限切れをcommit直前に再検査する保証ではない。既存の10秒deadlineは操作時間を制限するが、全操作と並行失効を直列化するものではない。本番で必要な強い失効境界は別途設計・検証する。

更新にはsessionとoriginに対応したCSRF tokenを要求する。商品名は既存の長さ・空文字・NUL制約を使い、JSONの未知キー・重複キーも拒否する。存在しない商品とアクセスできない商品には同じ固定404を返し、認証情報・SQL・入力値をエラーへ含めない。認証対象の応答はno-storeとする。

テストfixtureのmembershipをHTTPで作る機能や、Workspace/GoogleをSaunaログインへ代用する経路は追加しない。ローカルの既存DB・volume・サービスは保持し、テストは所有するfixtureだけを片付ける。

## Alternatives

- facility IDとログイン済みidentityだけで検索すると、施設間の権限を検証できない。
- membershipだけを検査すると、一度取得したsubjectがセッション失効後も利用される危険があるため、HTTP経路ではlive sessionもstatement内で検査する。
- Workspace設定の完了までHTTP境界を未検証にする代わりに、明確なローカル限定で否定ケースを先に確認する。本番化には所属・退職・権限失効の別検証が必要になる。

## Verification and limits

二施設で同じ商品UUIDを用い、一覧・詳細・更新の越境拒否、権限roleの差、所属とセッションの失効、credential無効化、Origin/CSRF、不正入力、拒否時のデータ不変を実PostgreSQL/HTTPで検証する。実行結果はAPIのPRに記録し、テストの設計だけで実行済みとしない。

独立Review/Security Review、実build/test、必須CI、GitHub Codexの指摘対応と最新HEAD再レビュー後にマージする。通常CIにおけるDB非接続テストのskipは、ローカル実DB検証と区別する。Atlas replay/drift CI、Workspace所属認可、本番公開、公開商品カタログ、管理画面の完成を意味しない。

WikiのArchitecture索引はsourceとして更新し、別repositoryへの公開実施とは区別する。
