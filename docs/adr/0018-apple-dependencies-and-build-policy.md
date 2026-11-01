# ADR-0018: Apple向け依存catalogとビルド設定

Status: Accepted for local build configuration / 2026-11-01

## Context

ユーザーはApple向けに以下の依存の事前追加と、APIと同じSwift compiler policyを指定した。利用者向けは既にセッションlibrary/test hostを持つが、管理者向けはまだアプリ未配置である。依存宣言・解決・自前コードのcompileを、各依存のruntime機能実装やnative Passkey完成と混同しない。

## Decision

両Appleリポジトリに次のcatalogを登録する。既存の互換exact pinを重複登録したり、指定下限へ無意味に下げたりしない。

| Repository | 指定条件 |
| --- | --- |
| [apple/swift-http-api-proposal](https://github.com/apple/swift-http-api-proposal) | main |
| [square/Valet](https://github.com/square/Valet) | from 5.0.0 |
| [sindresorhus/Defaults](https://github.com/sindresorhus/Defaults) | from 9.0.0 |
| [gohanlon/swift-memberwise-init-macro](https://github.com/gohanlon/swift-memberwise-init-macro) | from 0.6.0 |
| [apple/swift-http-types](https://github.com/apple/swift-http-types) | from 1.0.0（既存1.8.0 pinを維持） |
| [apple/swift-algorithms](https://github.com/apple/swift-algorithms) | from 1.2.0 |
| [apple/swift-async-algorithms](https://github.com/apple/swift-async-algorithms) | from 1.0.0 |
| [apple/swift-collections](https://github.com/apple/swift-collections) | from 1.1.0 |
| [fumoboy007/swift-retry](https://github.com/fumoboy007/swift-retry) | from 0.2.4 |
| [mtj0928/swift-async-operations](https://github.com/mtj0928/swift-async-operations) | from 0.5.0 |

`main`も解決revisionをlockfileへ固定し、通常build/CIはforced resolutionを使う。今回のproposalは`dff8847b09af6ea70b30472bd5c5bc91dd86c830`で、一次manifestがCollections1.7.1等をexact要求する。これに伴う既存pin更新は、任意downgradeではなく指定されたgraphへの整合である。webのcached main表示ではなく、実際に解決したimmutable commitを監査の正本にする。更新時はrootとXcode側の実product pinsを照合する。

自前targetに次の6 upcoming featuresを有効化し、default isolationをnil、strict memory safetyを有効にする。APIで既に用いるpolicyを参考にwarningsをerrorとして検証する。依存側へ同flagsを強制しない。

```swift
.enableUpcomingFeature("ExistentialAny"),
.enableUpcomingFeature("InternalImportsByDefault"),
.enableUpcomingFeature("MemberImportVisibility"),
.enableUpcomingFeature("InferIsolatedConformances"),
.enableUpcomingFeature("ImmutableWeakCaptures"),
.enableUpcomingFeature("NonisolatedNonsendingByDefault"),
.defaultIsolation(nil),
.strictMemorySafety(),
```

公開Foundation型は明示的なpublic importで表し、OpenAPI生成物を手編集しない。SwiftPM設定だけでは別のXcode host/test targetへ継承されないため、そのtargetにも対応する設定を適用し、実際のcompiler invocationとiOS SDKで検証する。未適用targetまでpolicy済みと呼ばない。

strict検査で検出された保存payloadのunsafe bytes使用は、同じ49byte/version/時刻/32byte token形式を保つbig-endian shiftに置換し、旧形式のgolden dataとの互換をテストする。POSIX pointerを用いたloopback fixtureはNetwork.frameworkへ移し、loopback限定・受信上限・timeout・取消の境界を維持する。無根拠なunsafe/@uncheckedによる抑制は追加しない。

iOSの`SecItemCopyMatching`だけはApple C APIの同期out parameterを必要とする。初期化したlocal `CFTypeRef?`へのpointerが呼出し期間を越えてescapeしないことを根拠に、製品コードの1呼出しと同APIを直接検証するSimulator専用の2呼出しに限って、call expressionを`unsafe`として明示する。scope/attributes/status/所有権とCAS検証を変更せず、function全体や外部依存へのunsafe設定・警告抑制へ拡大しない。これはC interop境界の明示であり、依存不具合の暫定回避ではない。実SecItem検証は専用Simulatorだけで行う。

## Security and runtime boundary

Valetは依存宣言だけであり、既存のThisDeviceOnly/iCloud同期なし/namespace/revision CASを持つKeychain providerを暗黙移行しない。Defaultsへtoken・CSRF・権限や本人確認状態を保存しない。memberwise macroをopaque token/lease/ticketへ適用して構築制約を開かず、Retry/AsyncOperationsをspent nonceや非冪等な認証操作へ自動適用しない。

未使用productを無理に配線しない。依存解決はmanifest評価を伴うが、すべてのmacro executableやlibrary productをcompile・実行・監査済みとは言わない。macro/toolのsandbox無効化やcredential権限拡大を加えない。

管理者repoの最小foundation targetはcompiler設定を実証する段階であり、管理UI・社員のWorkspace対応・施設認可・Passkeyを実装したとは扱わない。施設UUIDの参照値は、所属や業務権限を表さない。

## Project format and validation

Xcode27.2の標準に合わせ、test harnessの設定は公式JSON `project.xcproj`を用いる。公式`xcodebuild -convert-project 'Xcode Project'`で移行し、SwiftPM参照・target/scheme IDs・全Debug/Release設定・test host/ad-hoc/空Teamを保持する。旧形式の併置や独自の未検証converterを作らない。Apple公式format libraryによるroundtrip、意味比較と実build/testを行う。詳細は[移行PR](https://github.com/sauna-studio/sauna-app/pull/15)を参照する。

catalog/compiler policyは[利用者Issue13](https://github.com/sauna-studio/sauna-app/issues/13)と[管理者Issue6](https://github.com/sauna-studio/sauna-admin-app/issues/6)で追跡する。実resolve/build、既存host tests、該当iOS SDK/専用Simulator、独立Review/Security、最新Codex再レビュー、全CIの結果をそれぞれのPRへ記録する。管理者repoのUI/test未配置を成功扱いにしない。

Apple Developer・所有RPドメイン・Team/Bundleは未設定である。アカウント登録、署名鍵・証明書生成、課金・本番公開をこの決定で許可しない。host既存Keychainには触れず、稼働中API/Web/DBを停止・初期化しない。検証用fixtureは自分で記録した所有UUIDだけをcleanupする。native Passkey UI/AASA・本番domain・実機のData Protection確認は別の工程として残す。

## References

- [API compiler policyの背景](0010-blindlog-api-reference.md)
- [Apple保存契約](0015-apple-session-storage-contract.md)
- [Apple API再検証](0017-apple-session-api-client.md)
- [Apple公式project format](https://developer.apple.com/documentation/xcode/updating-your-xcode-project-configuration-file-format)
- [公式format library](https://github.com/apple/xcode-project-format)
