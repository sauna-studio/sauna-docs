# ADR-0023: 公開商品カタログと設定済み利用条件

Status: Proposed / 2026-11-01

## Context

[API Issue16](https://github.com/sauna-studio/sauna-api/issues/16)は、貸切・共用サウナ、日帰り・宿泊テントの一覧・詳細と利用条件の検証を求める。既存productsにはkindとpublishedがあるが、定員・利用時間・泊数を保持する条件は未定義だった。実施設の営業時間・料金・定員はまだ提供されていない。

## Decision

新しいproduct_offeringsへ、施設と商品を含む複合key、商品kind、定員、利用時間の上下限、泊数の上下限を保存する。products側の施設・商品・kindのunique制約と複合FKで対応を強制し、商品kindだけを変更して条件を取り違えられないようにする。既存SQLを改変せず、新しいAtlas migrationで追加する。既存商品の条件を推測してbackfillしない。

定員・利用時間は正のInt32範囲とし、上下限の逆転を拒否する。非宿泊商品は泊数0、宿泊テントは正の泊数範囲を要求する。これらは型と整合性の技術上限であり、実施設の営業方針や推奨値ではない。人数定員と在庫数を区別し、泊数を24時間の単純な倍数と決めつけない。

匿名の一覧・詳細は既存products.published=trueかつ条件が設定済みの商品だけを返す。公開状態を表す重複fieldや、未定義の施設active状態を新設しない。既存に施設の営業停止modelはないため、施設の休業・閉鎖を反映できるとは主張しない。公開routeの例外は認証middlewareの明示的な2 operationに限定し、staff routeの保護を広げて解除しない。

公開DTOは施設・商品ID、名前、種別、条件と公開状態に限定する。価格・通貨・在庫残数・営業calendar・staff情報・PIIを含めず、検索結果を予約や決済額の保証と扱わない。匿名のdraft・欠落商品は同じ固定404とし、公開状態を任意指定してdraftを照会する経路を作らない。

staffのdraft照会と条件設定は既存のstaff origin、信頼済みsession、各SQLでの有効session/credential/membership/role照合を要求する。書込みはowner/managerとCSRFを必須にし、商品kindをクライアントの値へ変更しない。条件と既存publishedの更新は1 transaction内で原子的に行い、不正条件や拒否時に公開状態だけを変更しない。重複・未知JSON/query parameterも拒否する。

既存のtransaction/deadlineとREAD COMMITTEDの境界を維持する。COMMIT直前の取消検査、ロック待ちの遅延commit否定、COMMIT応答喪失時の結果不明を区別する。Workspace確認済み社員の本番認可は別Issueで継続する。

## Local validation database

既存DBへ新schemaを先に適用せず、新しいApple containerのDBでSwift実接続テストを行う。承認済みlocal app passwordを同じ用途だけに再利用し、新しい秘密値を生成しない。単一credentialの私有copyを0700 directory/0600 fileでreadonly mountし、admin credentialやrepository全体は渡さない。コピーは初期化後に除去する。

helperは秘密情報を読む前にschemaをPostgreSQL ASTで検査する。psqlの単一backslash commandとして解釈されない固定SQL prefixも使い、metacommandによるOS実行を許さない。adminの接続はpeerのみ、host側は新規のloopback port55433だけを使い、使用中portを奪わない。cleanupは新しいUUID/所有labelが一致するVMに限定する。

このSwift用DBはcanonical schemaから準備する。Atlas migrationのfresh replay・再適用・schema parityは、別の隔離harnessと必須CIで検証し、schema直接適用をmigration適用の証拠と混同しない。既存DB・volume・稼働サービスはresetしない。

## Verification and limits

四種類と二施設のfixtureで公開・draft・kind filter、一覧・詳細、role/session/CSRF、不正条件・kind変更・複合FK・拒否時の不変性を実HTTP/PostgreSQLで確認する。実行結果はAPI PRへ記録し、文書の提案だけで検証完了としない。

後続Issue17の在庫、Issue18の価格・営業日・時間帯、Issue19以降の空き状況・予約・決済はこのカタログだけでは完成しない。実施設の値や課金方針を架空のfixtureから本番設定へ転用しない。
