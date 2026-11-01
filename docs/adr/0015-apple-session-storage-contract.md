# ADR-0015: Appleクライアントのセッション保存契約

Status: Proposed / 2026-11-01

## Context

API Issue13のWeb cookie/CSRFと本人Passkey管理は実装済みだが、Appleアプリの安全なtoken保存契約は残っている。利用者・スタッフの両アプリはまだ基盤段階であり、Associated Domainsや本番RP、実端末の登録・loginを検証済みと扱うことはできない。保存機構を先に独立したlibraryとして検証する。

## Decision

初めてのApple実装をsauna-appのSwiftPM library `SaunaAppleSession`へ置く。Foundation/Securityを使い、iOS・iPadOS27.2を対象にする。admin側も同じprofile分離契約に従う。まだ存在しないadminクライアントへの依存配線を作ったり、二つのアプリで実認証を検証済みと表現したりしない。

tokenは32-byteのcanonical base64url値をopaqueな型として扱い、description/debugDescription・エラーに値を出さない。Keychainにはtokenと保存期限等の最小データだけを保存し、CSRF値はメモリだけに置く。UserDefaults、通常ファイル、共有cookiejar、iCloud同期へ認証情報を複製しない。

Keychainは`WhenUnlockedThisDeviceOnly`と非同期cloudの属性を指定し、accessgroup共有を使わない。このclassは端末のunlock状態を必要とし、別端末へのバックアップ復元でitemを移行しない。Simulatorの属性照合だけで実端末のData Protectionやハードウェア保証を実証したとは表現しない。

環境とcustomer/staffをKeychain namespaceに束縛し、読取・更新・削除は正確なscopeだけを対象にする。現契約は各環境に単一backendを対応させ、cookie受理をlocal固定originへ制限する。origin文字列自体は保存account名に含まないため、将来同じ環境へ複数backendを導入する場合は、既存sessionを別backendへ転用しないscope拡張が必要になる。期限切れやlogoutでtokenを破棄する。locked、not found、破損、削除失敗を同一視せず、削除に失敗したのに成功と返したり同一processで古いtokenを復活させたりしない。server失効・401等の結果は要求の世代に束縛し、遅い応答や別writerが保存した新しいsessionを古い処理で消さない。

local cookie契約の受理は固定API `http://127.0.0.1:8080`とprofile別の`__Host-`名、正当なoperation/status、単一header、Domain無し、Path=/、Secure/HttpOnly/SameSite=Strict、期限、token形式を照合する。任意URLからのcookieを保存しない。本番originは未設定として拒否し、HTTPの許可を本番や他hostへ拡大しない。

URLSession factoryはephemeral設定とし、cookie・credential・cache storageを共有せずredirectを拒否する。factory単独では初回requestのURLを制限したりtokenを自動添付したりしない。将来のnative clientでtokenを添付する時は、宛先を信頼済みscopeへ固定するrequest builderを別途検証する。保存tokenの存在やローカル期限だけでは認証済みと判断せず、権限と失効の正本はSauna API/PostgreSQLとする。この段階のfactory/受理検証を、完成したnative認証clientと呼ばない。

## Validation and safety boundary

host unitはfake persistenceだけを使い、host既存Keychainへアクセスしない。実SecItemのadd/read/update/delete・属性・profile/environment分離・古いrevisionでの更新/削除拒否は、専用iOS27.2 Simulatorとテスト専用namespace・合成tokenで確認する。実アカウントや実鍵、Apple development証明書は使わない。並行writerの保証範囲とOSによる制限は実測に応じて文書化する。

期限切れ・logout・locked/error・late応答・破損データ・unsupported version/nonfinite期限、cookie受理の負例、redirect拒否をテストする。独立Review/Securityと最新Codex/CIは、ローカル実行結果に加えるmerge条件である。未実行のSimulator、ネットワーク、実端末確認は明示する。

ローカル初回実測ではhost22件が成功し、独立Review/Securityも別snapshotのfake-only host検証22件を成功させた。専用iOS27.2 Simulatorでは実KeychainのXCTest6件と同じSwiftTesting22件が成功した。最初の未署名・unhosted実行は`errSecMissingEntitlement`となったため、必要なアプリ識別を持つ非UI testhostとad-hoc署名へ切り替えた。実証明書、Apple Team、秘密鍵、共有accessgroup、host Keychainは使わず、保存属性も弱めていない。最新commitのCI/Codex結果は実装PRへ別に記録する。

## Alternatives and consequences

通常のHTTPCookieStorageへ任せる方法は共有・永続化先と消去範囲を制御しにくいため採用しない。全Keychain itemを消すlogout、client側の保存状態を業務認可へ使う方法、古い401で新sessionを削除する方法も採用しない。

ThisDeviceOnlyにより端末移行時は再loginが必要になる。Passkey自体の同期・バックアップは認証器の機能であり、session保存とは別物である。実nativePasskey登録、Associated Domains、本番署名、全喪失回復は別の受け入れ条件として残す。

## References

- [API Issue55](https://github.com/sauna-studio/sauna-api/issues/55)
- [API Issue13](https://github.com/sauna-studio/sauna-api/issues/13)
- [Appleアプリ認証Issue2](https://github.com/sauna-studio/sauna-app/issues/2)
- [Apple Keychain accessible class](https://developer.apple.com/documentation/security/ksecattraccessiblewhenunlockedthisdeviceonly)
- [Apple ephemeral URLSession](https://developer.apple.com/documentation/foundation/urlsessionconfiguration/ephemeral)
- [Passkey管理の境界](0014-passkey-management-and-recovery-boundary.md)
