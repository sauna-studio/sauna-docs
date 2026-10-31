# ADR-0012: ローカルPasskey登録・署名検証・セッション

Status: Proposed / 2026-11-01

## Context

ADR0009で保護したVerifiedSubjectの生成元を実装し、localhostの利用者WebとスタッフWebから実際のWebAuthn ceremonyを検証する。Google Workspace所属確認は別の認可条件であり、Passkey認証だけでスタッフ業務権限を与えない。この決定はADR0009の「認証producer未実装」の段階を更新する。実装・依存PRのマージと本番対応の承認は別に扱う。

## Decision

WebAuthn検証・challenge・credential・sessionのproducerをSaunaAPIIdentity内へ置き、VerifiedSubjectのinitializerをinternalに保つ。SaunaAPIDatabaseからIdentityを参照し、循環依存や公開の未検証subject factoryを作らない。公開HTTP契約はOpenAPIを正本とする。

匿名登録はserver生成のuser ID/32-byte user handleを新規accountへ結び付ける。既存accountを選択する登録は提供しない。登録成功だけではsessionを発行せず、署名・UVを検証したログインを要求する。none attestation・ES256/P-256・resident credential・UV requiredに限定し、RP、origin、type、nonce、UP/UV、credential identity、COSE鍵、user handle、BE/BSを検証する。sign counterは双方ゼロなら許容、それ以外は増加を要求し、credential row lock内でcounter更新とsession発行を原子的に行う。BEは変更を許さず、BSがBEを超える状態も拒否する。

challengeは署名検証前に独立したautocommitで消費し、その後の失敗で復活させない。credential公開鍵はDBへ保存し、秘密鍵はサーバーへ送信・保存しない。raw JSONの重複key・上限・深さを検査する。CollectedClientDataはW3C仕様に従い未知propertyを許容するが、必須property・crossOriginは厳密に検証し、ローカルadapterではtopOriginとcrossOrigin=trueを拒否する。元clientDataJSONを再構築せず署名検証へ渡す。CBORの入力長・構造をdecoder前に制限する。

sessionはCSPRNGの32-byte tokenを発行し、DBはSHA-256 digestのみ保存する。active credential・所有user・origin・DB時刻の有効期限・失効を毎回照合する。Webのflow/session cookieはprofile別の__Host名でSecure/HttpOnly/SameSite=Strict/Path=/を付ける。logout/revoke-allはsession tokenからドメイン分離して導出したHMAC CSRF tokenを検証する。token本体はJSONへ返さず、CSRF値はWebのメモリに保持する。JavaScriptからsession cookieを参照させない。

SvelteKit/Bun BFFは自profileの正規origin/Hostを固定し、許可した7つのAPI pathだけをproxyする。任意URLへ転送しない。origin・Fetch Metadata・cookie重複を検査し、body上限と共通deadlineを設け、redirectを追従せず、固定JSONエラー・no-storeを返す。Bun adapterのorigin推論へ依存せずKitのpaths.originを明示する。ブラウザー標準のJSON変換APIを使い、不要な互換shimを増やさない。

DB処理は共有poolを維持し、deadline時に所有するleaseだけをcloseする。close完了を待ってからleaseを返し、遅延cancelが次の借用者へ影響しないようMutexで完了とcancelを直列化する。Taskのcancelを伴わないCancellationErrorでも接続を破棄する。transaction cancelでは接続を切断し、close完了を待ってleaseを返す。server側は切断検出時に未commit transactionをrollbackする。closed channelへROLLBACKを再投入せず、serverからのrollback応答を待ったとは扱わない。通常errorはrollbackし、rollback失敗時には接続を破棄する。driverのclosed-channel query promise問題は既存上流PR487/501を踏まえ別途検証・最小修正する。

## External libraries and delivery

blindlog-apiの固定参照に従いSwiftの厳格検査を有効にする。ユーザー指定のswift-postgresql fork/PostgresNIO traitとswift-sqlのtyped projection・bind値を既存async transaction上で使用する。外部ライブラリの最小修正は独立fork/PRとlockfileのrevisionで追跡する。SwiftCBORは既存上流PR120の最小修正と原作者を保持し、重複した上流PRを作らない。

swift-webauthn add-initへmainを取り込むPRとCrypto5互換修正を用意した。検証中は未mergeの公開PR refを明示して積み重ねる場合がある。最終採用はadd-initへ戻して再resolve・build・test・レビューする。GitHub Codexの利用上限・失敗は指摘なしと見なさず、CI成功と最新HEADの指摘なし確認までマージしない。

## Alternatives

Googleログインをsession認証に使う案、登録だけでログイン済みにする案、client userIDからsubjectを作る案は不採用。cookieをlocalStorageへ複製する案、ブラウザーの署名対象JSONをserverで再構築する案、無署名のfixtureだけで検証する案も不採用。SQL cancelのために共有pool全体を停止する方法は他リクエストへ影響するため採用しない。

## Validation and remaining work

公式WebAuthn main固定版でhost Swift65testsを実PostgreSQL18接続で実行し、独立Security Agentも同じ65件を再実行して成功した。query/transaction deadline、rollback、CancellationErrorだけをthrowする経路とpool再利用を含む。Python28testsとschema parity・migration過去改変guardも成功。

Bun production adapterと実APIを使うChromium resident/UV virtual authenticatorで、利用者の登録・署名ログイン・reload・logout・revoke-allとスタッフのログイン準備/匿名登録拒否/Workspace未認可を各3回検証した。鍵・cookie・credentialのexport、trace/video/screenshot/HARを行わない。実Apple端末のPasskeyは未検証である。

依存の最終revisionによるbuild・Linux test・GitHub CI・最新Codex結果は実装PRへ記録する。追加credential/削除の再認証、account recovery、Appleのtoken保存契約、Workspace本人対応・施設業務HTTP認可、production RP/HTTPS・共有rate limitは後続Issueの対象であり、API Issue13全体の完了とは扱わない。本番デプロイ・外部API認証情報の生成は行わない。

## References

- https://github.com/sauna-studio/sauna-api/issues/11
- https://github.com/sauna-studio/sauna-api/issues/12
- https://github.com/sauna-studio/sauna-api/issues/13
- https://github.com/zunda-pixel/blindlog-api/blob/82a13ed73fff44984e8954781d669cf8320883ea/Package.swift
- https://www.w3.org/TR/webauthn-3/#dictdef-collectedclientdata
- https://github.com/zunda-pixel/swift-webauthn/pull/1
- https://github.com/sauna-studio/SwiftCBOR/pull/1
- https://github.com/valpackett/SwiftCBOR/pull/120
- https://github.com/vapor/postgres-nio/pull/487
- https://github.com/vapor/postgres-nio/pull/501
