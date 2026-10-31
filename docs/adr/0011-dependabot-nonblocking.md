# ADR-0011: Dependabotを作業のブロッカーにしない

Status: Accepted / 2026-11-01

## Context and decision

ユーザーがsauna-api#41を示し、Dependabotは無視してよいと指示した。Dependabotの失敗・通知を対応対象/作業のブロッカーから除外し、updaterの復旧待ち・そのためのSwift要件引下げは行わない。

依存変更は差分とPackage.resolved/lockfileをレビューし、通常のbuild/test/required checksとGitHub Codexレビュー条件を引き続き適用する。今回の作業はlocal-onlyであり、GitHub上のIssue状態や設定の変更は行っていない。

## Reference

- https://github.com/sauna-studio/sauna-api/issues/41
