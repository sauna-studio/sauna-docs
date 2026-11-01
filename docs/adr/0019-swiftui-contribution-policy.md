# ADR-0019: ユーザー指定SwiftUI指針の管理

Status: Accepted for contribution policy / 2026-11-01

## Context

ユーザーが4本の記事をSwiftUI作業時の規則・tipsとして指定した。記事には2023年の実装例と過去SDKでの測定も含まれる。対象OS27.2以上、現在のcompiler policy、Appleの契約と整合する判断基準として扱い、古い例のコードや推測を無条件に取り込まない。

## Decision

正本は[専用policy](https://github.com/sauna-studio/.github/blob/main/policies/swiftui.md)とし、[共通Issue17](https://github.com/sauna-studio/.github/issues/17)で管理する。対象はsauna-app/sauna-admin-appのSwiftUI作業だけで、一般core AGENTSや非SwiftUI7repoへ不要な変更を広げない。

正本をmainへマージ後、両iOS AGENTSへ本文を完全copyし、適用元main commitと内容hashを明示する。リンクだけの継承とは扱わない。共通Issueは正本PRだけで閉じず、両追従PRの最新レビュー・CI完了後に閉じる。

4記事は設計意図の参照とし、APIの現在の契約はApple一次資料、実装判断は利用可能なSwiftUI Expert Skillと照合する。プロジェクトのOS・セキュリティ要件をSkillの汎用助言より優先する。具体的な適用判断は正本へ集約し、このADRに別版の規則を複製しない。

## Verification and limits

正本とcopyのbyte一致、適用元commit、既存AGENTS本文とSource/Tests/manifest/pins/workflowの不変、参照リンクを検証する。独立Review/Securityと最新Codex再レビュー・必須CIも必要である。

文書反映だけでSwiftUI画面の実装・描画・性能検証を完了扱いにしない。現UIKit testhostの成功と実SwiftUI UIの検証も区別する。将来のUI変更では正本に従う対象SDK・表示・状態・遷移確認と、必要な実測を行う。

この決定は認証方式・セッション保存・API認可・権限を変更しない。Apple DeveloperやRPドメイン、署名・本番公開を設定する許可でもない。

## References

- [ユーザー記事: Layout](https://zenn.dev/zunda_pixel/articles/2cc489b4168a5a)
- [ユーザー記事: Identity](https://zenn.dev/zunda_pixel/articles/ea826f888d05ed)
- [ユーザー記事: Observation](https://zenn.dev/zunda_pixel/articles/9ce01609d0d234)
- [ユーザー記事: Navigation](https://zenn.dev/zunda_pixel/articles/ebf2a079cbf68b)
- [正本PR18](https://github.com/sauna-studio/.github/pull/18)
- [Apple build policy](0018-apple-dependencies-and-build-policy.md)
