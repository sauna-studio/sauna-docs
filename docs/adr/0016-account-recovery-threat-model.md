# ADR-0016: 匿名accountの全Passkey喪失をfail-closedに保つ

Status: Accepted for current local scope / 2026-11-01

## Context and user decision

複数Passkeyと本人の失効操作はAPI Issue53で実装した。残る全credential喪失時の回復について、ユーザーは2026-11-01に「既存方針を維持し、全喪失回復は設計・否定テストまで」と選択した。本決定では回復code、他の認証要素、回復endpointを生成・有効化しない。親Issue13の全喪失回復機能を完成したとは扱わない。

現在のaccountはserver生成UUIDとPasskeyの公開鍵に結び付く匿名accountであり、確認済み氏名・メール等の本人確認属性を持たない。後からGoogleアカウントやWorkspace所属、メール受信、スタッフへの申告だけで旧accountの所有者を特定する根拠はない。

## Current decision

使える予備Passkeyが残っていれば、それで署名・UV loginし、新しい予備keyを追加してから紛失keyを別keyで失効する。管理変更による全session失効、最後のkey保護、nonce/session/accountの束縛はADR0014を維持する。同期Passkeyのcredential数を物理端末数や独立した復旧手段の数と数えない。

すべてのPasskeyが使えない場合はアクセスを拒否する。cached sessionだけではkey追加の再認証を代替できず、別accountの正当なPasskeyも旧accountの証明にはならない。新規匿名登録をしても別accountであり、旧予約・決済・施設所属等を自動移管しない。サポートへの問い合わせは、account resetの認可や本人確認が完了したことを意味しない。

## Threat model and future alternatives

| 脅威・制約 | 判断・将来方式の必要条件 |
| --- | --- |
| 回復codeの窃取・phishing | codeで新key登録だけ許可しても、攻撃者が自分のkeyとUVを使える独立したreset認証要素になる。Passkeyと同じ保証とは呼ばない |
| 根拠のない事後本人確認 | 匿名accountへメール/Google/スタッフ申告を後付けして旧ownerの証明にしない。将来の本人確認方式には事前登録の根拠と独立した評価が必要 |
| 盗まれたsessionでkey追加 | 既存keyのfresh署名/UVを要求し、user/session/RP/origin/action/対象へ束縛する |
| 新keyの秘密鍵を持たないまま旧key全失効 | 将来回復を採る場合は、新keyのfresh署名/UVによるPoPを確認してから、旧key・全session・旧回復proof失効と新key有効化を同じaccount lock/TXで行う |
| 失敗・通信断・cancelで唯一の回復手段が消滅 | challengeの単一使用と、長期回復proofの最終消費を区別する。将来は有界なintent lease/再試行/取消を設計し、成功commit以外で永久喪失させない |
| 回復の競合・古いcode/intentの再利用 | 将来はaccount世代、rotation、期限、単一winner、旧pending intent失効をDBで保護する |
| 旧ownerからの防御手段を先に奪う | 将来の待機期間中は既存keyのfreshUVで取消・再発行できる設計を検討する。現状に実通知channelが無いので通知済み・ownerが検知可能とは主張しない |
| ログ・URL・画像による漏洩 | 将来proofを扱う場合もdigestのみDB、値はURL/ログ/trace/HAR/storageStateに残さず、公開Issueへ秘密値を載せない |

この表は将来方式の検討条件であり、回復code方式の採用や秘密生成の許可ではない。新しい回復方式を導入する場合は、保証の違いと本人確認・通知能力を具体化してユーザーの方針決定を得る。NISTの認証保証等を参考にしても、Saunaが特定AALに適合・準拠済みだとは主張しない。

## Executable boundary and evidence

追加する実DB負例は、本人の有効session/CSRFと正しい管理nonceに対して、別accountの正当に登録したkeyによる正しい署名/UVを提出してもkey追加を認可できないことを検証する。先に同じproofをそのkeyの正規公開鍵とuserHandleで暗号検証して成功させ、誤署名や不正originによる偶然の拒否ではないと確認する。

拒否後にnonce消費が維持され、authorizer/認可日時/登録nonceが未設定、本人の唯一keyとsessionが変わらないことを確認する。本人keyのproofでも同じspent intentは再利用できず、別fresh intentなら正当な本人keyが認可されるpositive controlも確認する。これは既存の管理境界の否定テストであり、存在しない回復endpoint全般の保証や回復機能の提供ではない。

fixtureは自分で作ったUUIDだけを追跡して削除し、既存のローカルDB・volume・ブラウザー利用者のデータをresetしない。公開の合成fixtureと既存承認済みのローカル仮想鍵・session検証だけを使い、新しい回復secretを生成しない。実行結果はAPI PRへ記録し、設計上の期待と実測を区別する。

## Consequences and follow-up

全喪失した匿名accountは現方式では復旧できない。この利用上の制限を隠さず、予備Passkeyの事前登録を案内する。既存session、予約や決済の所有者を曖昧な本人申告で移し替えない。

API Issue56は本決定・脅威モデル・否定境界の完了だけを追跡する。Issue13の回復機能全体とApple native認証の受け入れは別に残す。Wikiはsource索引を更新するが、未初期化のGitHub Wiki本体を公開済みと表現しない。

## References

- [API Issue56](https://github.com/sauna-studio/sauna-api/issues/56)
- [親Issue13](https://github.com/sauna-studio/sauna-api/issues/13)
- [既存管理Issue53](https://github.com/sauna-studio/sauna-api/issues/53)
- [Passkey管理の境界](0014-passkey-management-and-recovery-boundary.md)
- [OWASP Passkey lifecycle and recovery](https://cheatsheetseries.owasp.org/cheatsheets/Passkey_Security_Cheat_Sheet.html#account-recovery-and-bootstrap)
- [OWASP factor reset](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html#resetting-mfa)
- [OWASP offline recovery methods](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html#offline-methods)
