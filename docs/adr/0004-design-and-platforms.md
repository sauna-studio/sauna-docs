# ADR-0004: Vintage/Pumpkinと現行プラットフォーム

Status: Accepted / 2026-11-01

## Decision
利用者/管理者ともTweetbotのVintage (light) / Pumpkin (dark)を意匠の参考にする。参照リポジトリを確認した基本色はVintage accent #CC4400 / content #E6E2DA / subcontent #E0DACE、Pumpkin accent #FF6619 / content #292E33 / subcontent #1F2226。第三者画像や独自資産はコピーせず、色のトークン化とアクセシビリティ検証を別Issueで実施する。

iOS/iPadOS最小27.2、最新安定ブラウザを対象にし、不要な後方互換コードを増やさない。ローカルXcode27.2 / Swift6.4.2を確認。GitHub-hosted runnerのSDK availabilityはApple CI追加時に実際に確認し、存在しないrunner labelや旧SDKで代替した成功を記録しない。利用できない場合はAppleビルドの未検証を明記する。

## Reference
https://github.com/zunda-pixel/tweetbot/blob/main/TweetbotKit/Sources/TweetbotUI/Components/ThemePalette.swift
