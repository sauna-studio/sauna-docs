# ADR-0020: GitHub Actions workflow lockfiles

Status: Accepted for rollout / 2026-11-01

## Context

ユーザーはGitHub Actions workflow lockfilesのGA機能を採用するよう指定した。既存の完全SHA固定と最小permissionsを保持しつつ、推移的Action依存とupstream repository identity/provenanceを検証する必要がある。

## Decision

[共通Issue20](https://github.com/sauna-studio/.github/issues/20)で9repoの導入を追跡する。公式`github/gh-actions-lock` v0.4.0の`--no-narrow`で各repoの`.github/workflows/actions.lock`を生成し、既存のfullSHA `uses:`を保持する。生成物は手編集しない。規則・更新手順の正本は[共通policy](https://github.com/sauna-studio/.github/blob/main/policies/workflow-lockfiles.md)とする。

各repoにcontents: readの検証Workflowを配置し、固定releaseとSHA256を確認した公式Linux binaryで`--verify --no-narrow`を実行する。追加Secretsや権限拡大、pull_request_target実行、CIによる自動書換えは導入しない。検証はrepoファイルを変更しないが、ツール通常のuser-cache logは保存され得る。offline `--verify-local`はcoverageだけであり、networkを使うprovenance検証の代替としない。

共通Reusable Workflowの定義を先にlock導入してmainへmergeする。その後callerの`jobs.<id>.uses`をlock導入済みdefault-branch履歴commitのfullSHAへ更新する。job単位のReusable呼出自体はlockfile対象外で、その内部Actionは定義元commitのlockfileが担当する。caller側だけのlockfileでは旧source commitの依存は固定されない。

## Dependabot update cadence

追加のユーザー指定により、9repoの既存updates entryへ`cooldown.default-days: 7`を設定する。[Issue22](https://github.com/sauna-studio/.github/issues/22)で追跡し、既存schedule/ignore/PR上限等は保持する。これはversion release後の待機期間であり、weekly scheduleとは別の制御である。security updatesはcooldownの対象外で、セキュリティ修正を遅延させる設定ではない。新repo生成templateも同じdefaultを使用する。

## Verification and limits

生成の冪等性、既存Action commit/permissionsの保持、全Workflowのcoverage/provenanceを実測する。隔離fixtureで欠落entryと改変commitの拒否を確認し、元repo lockfileを変更しない。各PRは独立Review/Tool Security Review、最新Codex明示再レビューと必須CI成功後にmergeする。

Container image、runner image、その他tool download/build inputやActionの安全性全般は保証対象外である。既存digest/checksum controlsと依存のreviewを維持する。moved/unreachableなpinを無条件acceptせず、原因を確認してからPRで更新する。Dependabotの更新もreviewを省略しない。

この変更はOrganization全体のRequire lockfile強制ポリシーや課金・本番公開を設定する承認ではない。既存の認証・業務コード・Apple署名設定も変更しない。

## Alternatives

従来の直接依存fullSHA固定だけでは推移的Action依存やsource identityの同じ検査を提供しない。一方でWorkflowをmutable tagへ一括変更する必要はなく、公式`--no-narrow`で既存固定を保持できるため、不要な依存更新を避ける。

## References

- [GitHub GA announcement](https://github.blog/changelog/2026-10-28-github-actions-workflow-lockfiles-are-generally-available/)
- [GitHub lockfile concepts](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles)
- [Official generator](https://github.com/github/gh-actions-lock)
