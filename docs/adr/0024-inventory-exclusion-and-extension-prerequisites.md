# ADR-0024: 在庫の期間・席排他とDB拡張の前提管理

Status: Proposed / 2026-11-01

## Context

[API Issue17](https://github.com/sauna-studio/sauna-api/issues/17)は、貸切の排他、共用の定員、テント個体、施設境界と期間重複をDBで検証する。在庫数は商品カタログの一予約当たり定員と別の値であり、同じ物理サウナを貸切・共用商品から参照した場合も過剰確保を防ぐ必要がある。

## Decision

施設に属する物理resourceと商品対応、期間付きledger claimを分離する。UUIDをhashへ置き換えず、施設・resourceの正確なidentity、有限の半開時間区間[start,end)、席区間をGiST排他制約で検査する。共用はcapacity内の単一席区間、貸切とテントは全席を覆う非有界区間とし、共用同士の別席を許容しつつ、貸切と共用の競合もDBで拒否する。

resource type、product kind、capacityは施設を含む複合FKで整合させる。解放済みを含む履歴claimのFK参照が残る間はcapacity/typeを変更できない。将来のresize/version policyは別途設計する。enabled確認は有効なsession/member/roleとresource lockを伴う操作SQLで行う。別rowのenabledを単純なCHECKだけで検査できるとは主張しない。

今回の範囲は型付きstaff serviceとDBの在庫基盤とし、顧客の予約確定、hold TTL・支払待ち集約・価格・public空き検索・HTTP管理画面を完成した扱いにしない。実施設のresource数やcapacityを架空のfixtureから設定しない。

## Extension prerequisite

PostgreSQL18のbtree_gist1.8を、bootstrap所有の保護schema extensionsへ独立した前提設定として導入する。migration/dev/Swift testの新規owned DBだけで検証し、既存DB・本番へ無断で導入しない。appへCREATE DB/schema・superuser・server file権限を与えず、必要なUSAGEだけを許可する。

Atlas Community1.3.0はextension lifecycleを管理しないため、version・namespace・owner・拡張由来opclass・権限を独立SQLでfail-closed検査する。IF NOT EXISTSだけで正しい既存状態とは判断しない。public schemaのAtlas parityと、extension前提の検証は別の保証として明示する。管理外の境界と解消条件は[追跡Issue64](https://github.com/sauna-studio/sauna-api/issues/64)で保持し、導入PRから自動closeしない。

公式Atlas CEと新規peer-only PGで、事前導入したqualified UUID opclassを使ったgenerate/replay/reapply/public parity、共有席と貸切の排他、排他制約を除去したdriftの検出と残存を実証した。Pro account・token・課金は不要だった。このfeasibility確認を、在庫serviceや同時実行テスト全体の完成とは扱わない。

## Verification

同一期間の貸切・共用・テント、隣接時刻、同時INSERT、別施設の同一UUID、無効resource、kind/capacity/席範囲の不正、失効したstaffの操作、取消後の不変性を実PGで検証する。extensionのmissing/wrong version/owner/namespace/過剰権限も拒否する。実装・実行結果はAPI PRに記録する。

## References

- [Atlasの独立extension lifecycle](https://atlasgo.io/faq/manage-extension-only)
- [Atlas feature support](https://atlasgo.io/features)
- [PostgreSQL18 btree_gist](https://www.postgresql.org/docs/18/btree-gist.html)
- [PostgreSQL18 CREATE EXTENSION](https://www.postgresql.org/docs/18/sql-createextension.html)
