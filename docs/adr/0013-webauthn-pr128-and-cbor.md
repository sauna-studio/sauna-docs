# ADR-0013: swift-webauthn PR128とswift-cborの採用

Status: Proposed / 2026-11-01

## Context

最新ユーザー指示は、swift-webauthnの上流PR128を使用し、必要な独自修正をその上に自前fork branchで積み重ねることを明示した。PR128は従来のSwiftCBORからbrokenhandsio/swift-cborへ移行している。この指示によりADR0012のadd-init互換PR・SwiftCBOR forkの採用予定を更新する。過去の検証履歴は削除しない。

## Decision

上流PR128のhead `3fe310ab82b4c7dc5429ca3dbcc1308b3ff8abbb`を基点とし、祖先関係を保持した自前fork branch `codex/pr128-compat`を作成する。初期互換修正はCrypto許容範囲上限を5未満から6未満へ広げる1行と、Swift6.4が冗長と診断する外側のunsafe注釈2箇所の削除に絞る。内側のpointer操作のunsafe注釈と厳格compiler設定は維持し、独立レビュー・実テスト・PRで管理する。Linux実CIでFoundationEssentialsから文字置換APIが見えない問題を確認したため、最新ユーザー指示に従いBase64URLの文字置換をSwift標準のliteral collection `replacing(_:with:)`、padding追加を標準の`append`へ移す。runtime String用のFoundation追加importによる迂回は採用せず、Data変換に必要な既存FoundationEssentialsは維持する。公開ASCIIベクトルで+/とpadding0/1/2を検証し、正規形式のwire contractを変更しない。テスト用hex encoderもLinuxでのFoundation format bridgeを避けるため標準のradix16と先頭zero補完へ置換し、小文字・先頭zeroのgoldenで従来動作を検証する。現行APIが使用しないpublic Credential initializer追加を旧add-initから持ち込まない。上流PRが未mergeであることをlockfile・実装PRへ明示し、上流main採用済みとは表現しない。

APIの直接CBOR利用もproduct `CBOR`へ統一し、安定tag0.2.0、commit `52432a1118bcbabb9a973330c3af85d8ddf3f015`を使う。WebAuthnとAPIで同じpackage identityを解決し、旧SwiftCBORを新グラフへ残さない。以前のSwiftCBOR forkは上流PR120の修正を利用したfork・検証履歴として保持する。

`CBOR.decode`は入力全体の消費を検証し、`CBOROptions(maximumDepth:16,rejectDuplicateMapKeys:true)`をAPIで明示する。libraryの重複key拒否は既定falseのため既定値へ依存しない。既存の入力長・狭いattestation/COSE構造制限も維持する。旧decoderの残りbyte数検査用custom streamは新APIに置き換えて削除する。重複したattestation map keyの回帰を追加する。

PR128の非網羅enumや将来の未知エラーは固定された拒否/利用不可へ閉じる。署名対象clientDataJSONの元byte列、Origin/challenge/UV/credential所有の検証、session/施設権限の境界は変更しない。古いOSへの互換コードを追加せず、Sauna側の最新安定OS方針を維持する。

自前forkは最新安定compilerに合わせてtools minimumを6.4とする。Swift6.3と6.4で外側unsafe注釈の診断が異なることを実CIで確認したためであり、上流PR128本来の6.3対応とは区別する。compiler互換分岐や厳格検査の無効化は追加しない。

上流PR128のWebAuthnError struct→enum・39casesの旧static namespace廃止、COSE非網羅enum化等は意図的な公開API変更として採用する。main比較のAPI互換checkは維持し、上流変更に対応付けた122件の完全一致allowlistだけを使う。allowlist付き比較の成功と、1件を除いたnegative controlでその差分だけが失敗することを検証した。checkの全体無効化・任意wildcard・旧API shimは使わない。

## Alternatives

旧WebAuthn互換PRをmergeしてから新CBORへ独自全面移行する案は採用しない。上流PR128の既存変更を再利用し、patchを最小にする。二種類のCBORを同じ認証経路へ残す案、重複map key拒否を既定値に任せる案も不採用。

## Validation and remaining work

独立Security AgentがPR128差分とCBOR0.2.0のdecoder/depth/重複key設定を確認した。CBOR単体は91件とgenerative fuzz5件が成功、上流既定のdeep fuzz1件はskip。これはAPI consumerの検証とは区別する。

旧依存で成功したAPI65tests・実ブラウザー3反復を新依存の成功として流用しない。新forkのpackage tests、API build・PostgreSQL18統合・署名/UV/新CBOR回帰・境界compile probe、Bun BFF経由の実ブラウザー、Linux・遠隔CIを順に検証して実装PRへ結果を記録する。独立Review/Securityに加え、GitHub Codex最新HEAD指摘なしと必須CI成功までmergeしない。API keys・本番鍵・デプロイはこの変更に含めない。

## References

- https://github.com/brokenhandsio/swift-webauthn/pull/128/
- https://github.com/brokenhandsio/swift-webauthn/tree/3fe310ab82b4c7dc5429ca3dbcc1308b3ff8abbb
- https://github.com/brokenhandsio/swift-cbor/tree/0.2.0
- https://github.com/sauna-studio/sauna-docs/pull/8

文字置換APIの参照: [Foundation NSString](https://developer.apple.com/documentation/foundation/nsstring/replacingoccurrences%28of%3Awith%3A%29) / [Swift replacingのoverload](https://developer.apple.com/documentation/swift/rangereplaceablecollection/replacing%28_%3Awith%3Amaxreplacements%3A%29-1tg5u)。提示されたSwiftページはRegexComponent overloadであり、Base64URLの実装は文字列リテラルをcollectionとして渡すoverloadを使用する。Foundationをimportしない独立したSwiftコンパイルでも+/=をリテラル置換することを確認した。
