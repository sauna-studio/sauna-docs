# ADR-0017: AppleセッションのAPI再検証と送信先の固定

Status: Proposed / 2026-11-01

## Context

ADR0015の保存契約は、復元されたtokenを認証済みと扱わない。次の段階としてAPIの`GET /auth/session`と`POST /auth/logout`を接続する。native Passkey画面、Associated Domains、本番domain、実機の保護属性は別の受け入れ条件である。全Passkey喪失はADR0016に従いfailclosedを維持する。

## Decision

Sauna APIの固定commitのOpenAPIをsnapshotとして取り込み、出典とhash・更新手順を記録する。公式Swift OpenAPI Generator/runtime/URLSessionを使い、必要な2operationを生成する。生成コードを手編集せず、CIで再生成結果を照合する。手書きのJSON schemaや別の認証API契約を作らない。

public wrapperのscopeは保存vaultから得る。local backendは`http://127.0.0.1:8080`に固定し、production未設定は送信前に拒否する。生成client、任意URLやpath、Cookie・Origin・CSRFの自由な指定を公開しない。token添付前に最終送信先・method・operationとscopeを検証する。現在のAPIが要求するOriginはcustomerが`http://localhost:5173`、staffが`http://localhost:5174`であり、backend originとは別である。native HTTPにブラウザのCORSによる保護があるとは考えない。

transportは共有cookiejar・credential/cacheを持たないephemeral URLSessionを使う。今回の小さいJSON通信ではbuffered modeを明示する。公式transportのplatform defaultはDarwinでstreamingを選びtask delegateを設定するため、既存sessionのredirect拒否だけを根拠に安全と判断しない。生成clientから公式transportを通した実HTTPテストで、redirect先へ認証情報が送られないことを確認する。decode前のbody収集を16KiBへ制限するが、公式buffered transportはそれより先にwire body全量をbufferするため、ネットワーク受信メモリ上限ではない。固定local backend・10秒timeoutの今回範囲に限定し、本番・大きいbodyへ拡張する前にstreaming時のredirect制御と受信上限を再評価する。

復元leaseのtokenは固定`GET /auth/session`へ送る。200のUUID、期限、CSRF形式を検証し、保存期限を延長せず、同じgeneration/revisionのleaseだけにCSRFをmemory設定する。200にSet-Cookieは無く、session再発行とは扱わない。成功が遅れて到着しても新loginを上書きしたり、古い認証結果を現在の認証済み状態として返したりしない。

logoutは同一leaseのtokenとCSRFを使い、正しい204とprofile別削除cookieを検証する。削除は要求に使ったleaseだけを対象にし、await後の無条件な全local削除をしない。古い401やlogout成功が新loginのsessionを消さない。成功を返すにはremote応答とlocal保存削除の両方を確認する。失敗時はserver側の成否を確定したと表示しない。通信失敗・不正response・403/429/503をlogout成功としない。storage errorだけからremote失効の成否を個別に判別できるとは保証しない。

生成runtimeのClientErrorや低層errorはrequest/response、header、bodyを含み得る。外へは固定されたredacted errorへ変換し、raw underlying errorや認証情報を保持・出力しない。token、CSRF、leaseをdescription/reflectionから除外する。

## Validation and limits

正しいprofile/metadata/logoutに加え、scope違い、期限切れ、不正metadata/cookie、通信失敗、cancel、非成功status、遅い200/401/logoutと並行loginを検証する。host testsはfake persistenceを用い、既存host Keychainへ触れない。実SecItemとの組み合わせは専用iOS27.2 Simulatorだけで確認する。独立Review/Security、最新GitHub Codex再レビュー、全CI成功は追加のmerge条件であり、未実行項目は成功と記録しない。

ローカル実APIを確認する場合は、既に許可された一時仮想認証器・合成sessionだけを用いる。fixtureをappの通常保存方法にせず、値をログ・Gitへ出さず検証後に破棄する。既存API/Web/DBを停止・初期化せず、他のsessionや実利用者データへ触れない。

本件はセッション再検証とlogoutのclient契約であり、nativeアプリ全体の認証完成ではない。本番originの許可、AuthenticationServicesの登録/login/cancel UI、Associated Domains/AASA、実機でのData Protection確認を別途進める。

## Alternatives and follow-up

保存tokenだけで認証済みにする方式は失効確認を欠く。任意URLへ認証headerを付けるmiddlewareは送信先境界が広すぎる。共有cookiejarを有効にする方式も保存・消去範囲を制御しにくいため採用しない。

生成器のcookie搬送制約に対する明示adapterは[API Issue51](https://github.com/sauna-studio/sauna-api/issues/51)で追跡し、上流対応後に独立最小fixtureで再評価する。origin/operation/profile照合やredirect拒否は恒久的な安全境界であり、生成器更新だけで削除しない。

## References

- [Apple client Issue10](https://github.com/sauna-studio/sauna-app/issues/10)
- [保存契約](0015-apple-session-storage-contract.md)
- [全Passkey喪失の境界](0016-account-recovery-threat-model.md)
- [Swift OpenAPI Generator](https://github.com/apple/swift-openapi-generator)
- [Swift OpenAPI URLSession](https://github.com/apple/swift-openapi-urlsession)
