# ADR-0014: 再認証付きPasskey管理と回復の境界

Status: Proposed / 2026-11-01

## Context

ADR0012の新規登録・ログイン・session失効はAPI PR44で実装した。次に既存accountへ予備のPasskeyを追加し、不要なcredentialを失効できるようにする。session cookieを持つだけの攻撃者へ新しい認証手段を登録する権限を与えてはならない。全credential喪失時の回復を、この操作の例外として提供しない。

本決定はAPI Issue53（親Issue13）のローカル実装方針である。WebAuthnの登録・assertion検証は標準に従い、操作への束縛、上限、失効方針はSauna固有の安全設計として追加する。実装完了・実端末検証・本番導入をこの文書だけで認定しない。

## Decision

一覧は有効session本人のcredentialだけを返す。credentialの識別子と最小限の管理情報を表示し、COSE公開鍵・秘密鍵・他利用者の情報を公開しない。秘密鍵は引き続き認証器だけに保持する。

追加・失効はsessionとCSRF検証に加え、既存の有効Passkeyによる新しい署名とUVを必須にする。管理intentをaccount、session digest、RP/origin、操作、失効対象、nonce、DB時刻による5分以内の期限へ束縛する。intentと署名challengeは検証前に独立消費し、誤署名・取消・後続transaction失敗で未消費へ戻さない。通常login、匿名登録、別session、別操作のceremonyから転用しない。

追加は「既存keyで追加を認可するassertion」と「新keyを登録するcreation」の2段階に分ける。後段も独立nonceと単一使用状態を持つ。保存するuserHandleは既存accountのものを使い、クライアント指定userIDや任意の公開鍵を信用しない。最大10個の有効credentialをaccount単位で検査する。この上限は負荷と管理画面を有界にする製品方針であり、外部不具合の回避策ではない。

失効は記録を物理削除せずrevocationで扱う。対象と異なる有効credentialによる再認証を要求し、最後の有効credentialは失効できない。並行追加・失効・login・session失効でも、account単位の一貫したlock順序とtransactionで上限・所有者・有効性を再検査する。再認証後にsessionが失効した場合や、証明に使ったkeyが失効した場合も変更を拒否する。再認証のcounter更新と当該段階の認可・失効結果を原子的に保存する。二段階の追加保存は、有効session・key・intentを再検査した後段transactionで原子的に行う。

変更成功時は当該accountの全sessionを同じtransactionで失効させ、応答で現在のsession cookieを消去する。操作後は残るPasskeyで再loginする。sessionを継続するための別tokenや管理権限の持ち越しは導入しない。同時loginとの順序もaccount単位に定義し、変更以前のsessionが失効の対象から漏れないことを検証する。

## Threats and validation

| 脅威 | 必要な境界と回帰検証 |
| --- | --- |
| 盗まれたsessionだけでkey追加 | session/CSRFに加えて既存keyのfresh署名・UVを要求 |
| intentの転用・再送 | user/session/origin/action/target/期限を照合し、誤署名でも消費状態を維持 |
| 別accountへの登録・失効 | serverのaccount/userHandleを使い、credential所有者を同じtransactionで照合 |
| 最後のkey喪失・上限超過 | account lock下で並行変更と有効key数を検査 |
| 変更後も残るsession | session失効を変更と同じtransactionに含め、loginとの競合を実DB検証 |
| 取消後の部分commit・pool破壊 | 所有leaseだけを破棄し、非commit・後続pool再利用を検証 |

OpenAPIを契約の正本とし、生成コードを直接変更しない。実PostgreSQL18、Atlasの追加migration、crypto負例、HTTPのCSRF/origin/cookie、BFFと仮想認証器を別々に検証する。Coding中の独立ReviewとSecurity Review、最新commitのCodex指摘なしと必須CI成功をmerge条件とする。

## Recovery and alternatives

利用可能なPasskeyが残っている場合は、それでloginし、予備credentialを追加してから紛失credentialを失効する。同期Passkeyの複製は同じcredential IDを使う場合があり、credential数を物理端末数や独立した復旧手段の数と表示しない。同期先からの復元をSauna serverが保証することもできない。

有効Passkeyをすべて失った場合の本人回復は未提供とする。メールのみ、Google login、Workspace所属確認のみ、スタッフによる無審査の解除を代替認証として追加しない。既存予約・決済データを新accountへ自動移管しない。将来の本人確認・権限分離・待機期間・監査・異議申立て・旧session失効を含む脅威分析と実検証を、親Issue13の後続範囲に残す。

sessionの経過時間だけで再認証済みとみなす案、clientが送るaccount IDを使う案、最後のkeyを警告だけで削除する案、管理変更後に既存sessionをすべて維持する案は採用しない。操作数とUXの負担は増えるが、認証手段の変更と既存sessionの信頼を明確に分離する。

## Consequences and follow-up

対象はlocalhostの明示opt-in認証だけであり、スタッフのWorkspace・施設権限を与えない。Apple token保存契約、実Safari/Apple Passkey、本番RP/HTTPS、全喪失回復は未完のままである。親Issue13は本決定のmergeでは閉じない。

既存の暫定対処はAPI追跡Issue47〜51に記録している。管理実装で新しい回避策が必要なら、既存Issueとの重複確認後に理由・解消条件・再確認契機・回帰条件を追記する。恒久的な安全境界を回避策と一緒に削除しない。

Wikiにはexport用索引を更新する。GitHub Wiki自体は未初期化であり、source索引の変更だけをWiki公開済みと表現しない。

## References

- [API Issue53](https://github.com/sauna-studio/sauna-api/issues/53)
- [親Issue13](https://github.com/sauna-studio/sauna-api/issues/13)
- [API PR44](https://github.com/sauna-studio/sauna-api/pull/44)
- [WebAuthn登録の検証](https://www.w3.org/TR/webauthn-3/#sctn-registering-a-new-credential)
- [WebAuthn assertionの検証](https://www.w3.org/TR/webauthn-3/#sctn-verifying-assertion)
- [既存認証設計](0012-local-passkey-authentication.md)
