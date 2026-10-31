# ADR-0009: 認証subjectの生成境界とchallengeの原子的消費

Status: Accepted / 2026-11-01

## Context

ADR0008の複合FKだけでは施設ごとの閲覧/更新を認可できない。Passkey/sessionによる認証は後続実装だが、未認証のuser IDから認可contextを作る経路を先に用意すると迂回につながる。WebAuthn challengeは多instanceでも期限と一度だけの消費を守る必要がある。

## Decision

`SaunaAPIIdentity.VerifiedSubject`は別moduleとし、internal initializerだけを持つ。Decodableや公開の無検証factoryは付けない。現在はtestsが@testable fixtureを作り、認証producerは未実装のままとする。業務HTTPへ未認証userIDや任意headerを変換する経路を追加しない。

`FacilityStore`は各read/write SQLでsubject/membership/active status/role/facilityを再検査する。subjectの施設やroleをキャッシュしない。staff閲覧、manager/owner更新を最小ルールとし、missingとdeniedを同一固定エラーにする。READ COMMITTEDの次statementへの失効反映と、並行失効/操作の厳密直列化を区別する。Workspace社員確認はまだ行わず、公開管理APIへ接続しない。

challengeはPostgreSQLを正本とする。32-byte公開nonceと独立browser-flow bindingをCSPRNGで生成し、bindingはSHA-256 digestのみ保存する。RP/origin/purposeと最大5分の期限に結び付け、同一SQL statementでrow lockを取得後、fresh DB時刻を一度取得して原子的に消費する。消費済み状態を署名検証失敗時に戻さない。challenge成功を本人認証やVerifiedSubject生成とみなさない。

ローカルRPはlocalhost、customer/staffは別originとする。production設定・cookie/CSRF/rate-limit・credential追加の再認証済user/sessionへの束縛は未実装。ユーザー承認はローカル仮想認証器鍵と専用token生成のみで、外部APIや本番鍵へ拡張しない。

## Alternatives

client userIDをそのままsubject constructorへ渡す案、事前membership検査の後に施設条件なしでqueryする案、roleを長期間contextへキャッシュする案は採用しない。challengeのprocess内mapやread→deleteの二段階処理も、多instanceと競合に弱いため採用しない。transaction開始時刻now()やlock待ち前の時刻を期限判定に用いない。

## Validation

外部Swift moduleからsubject生成とJSON decodeがcompile拒否されることを実検証。二施設同productID、非member/失効/降格、staff更新拒否を実DBで検証した。challengeは誤RP/origin/purpose/binding、期限/再送、16並行消費で1成功、lock待ちで期限超過するケースを確認した。host Swift38testsとPython26testsが成功、独立Review/Securityを実施した。

API Issue9/10/15全体の完了、Passkey署名/UV・session・Workspace認可の実装済みとは扱わない。今回もローカルbranch/commitのみで、遠隔CI/GitHub Codexレビューは未実施。実行結果はsauna-api/docs/LOCAL_IDENTITY.mdとLOCAL_VALIDATION.mdに残す。

## References

- https://github.com/sauna-studio/sauna-api/issues/9
- https://github.com/sauna-studio/sauna-api/issues/10
- https://www.postgresql.org/docs/18/transaction-iso.html
- https://www.postgresql.org/docs/18/functions-datetime.html
- https://www.w3.org/TR/webauthn-3/
- https://github.com/apple/swift-crypto
