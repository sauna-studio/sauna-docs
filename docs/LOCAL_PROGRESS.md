# ローカル開発状況 — 2026-11-01

## 実装した基盤

- sauna-api: Hummingbird実HTTPサーバ、OpenAPI生成契約、PostgresNIOローカル接続pool/診断、Apple container build/runとPostgreSQL18。
- sauna-web: 指定Bun/Svelte5スタック、Vintage/Pumpkin切替、非PII人数preview、生成OpenAPI型。
- sauna-admin-web: 同スタックのreadonly shell。認証・管理操作は未実装。
- .github / sauna-docs: Apple container・Web stackのADRとエージェント規則。

今回の変更はcodex/*ローカルブランチに保存し、push・新規PR・GitHub Actions・本番deployは実施していない。以前完了したGitHub基盤と今回のローカル検証は区別する。

## アクセス

- API: http://127.0.0.1:8080/health と /version
- 利用者Web: http://127.0.0.1:5173
- 管理者Web: http://127.0.0.1:5174
- DB: 127.0.0.1:55432、sauna_local / sauna_app（ローカル専用）

起動中processを終了した後の再起動手順は各repoのdocs/LOCAL_DEVELOPMENT.mdを参照する。Webのpreviewは予約・決済の完了を意味しない。

## 検証

APIはhost Swift25tests（実DB4件を含む）、Python16testsとOpenAPI4examples、Apple containerのLinux release build/testを実施。Linuxはsecretを渡さずDB4件をskipし21件成功。実HTTP、SIGTERM、DB停止/再起動、timeout/cancelと回復も確認した。

両Webはfrozen install、型検査、lint、unit19件ずつ、production build、Playwright6件ずつ、実API smokeを成功。利用者フォームの競合修正後は追加60ケースも成功した。独立Review Agentが再実行し、Security Review AgentがDBのsecret/権限/所有資源保護を確認した。各repoのdocs/LOCAL_VALIDATION.mdに詳細を記録する。

DB passwordはユーザーが明示許可したローカル専用値のみ生成し、Git除外の私有ファイルに保存。値は記録しない。他のAPIキー・秘密鍵は要求も生成もしていない。

## ライブラリ方針と次の作業

公式のHummingbird/PostgresNIO/Swift OpenAPI、SvelteKitと指定Web libraryを利用。現時点でforkが必要な上流不具合は見つかっていない。必要になったら再現テスト、最小fork差分、固定revision、上流PRの順に追跡する。

業務schemaとAtlas migration、施設境界のDB制約・統合テストを追加した（ADR0008）。次はCI接続と認証済tenant context/API認可へ進む。Passkey、予約競合、Stripe、Workspaceは未実装。外部credentialが必要になった時点で確認する。Safari実機/iOS、リモートCI、本番環境は今回未検証。

## schema/migration追加段階

API Issue8/9のDB部分として6業務table、Atlas CE1.3.0の初回forward-only migration、trusted Git baselineの改変拒否、pglast8.7 ASTのDDL guardを実装。空replay DBへ適用/再適用、実drift列の検出/自動修復なし、実app接続SQL21拒否を成功。開発DBへ適用後のhost Swift25tests、Python26testsとOpenAPI4examplesも成功した。独立Review/Securityの未解決blocking指摘なし。

新しいcredentialは生成せず、承認済みlocal DB passwordをprivate一時configで利用した。app roleはDDL/owner/admin membership権限なし。複合FKによる越境参照拒否と、まだ未実装の施設別閲覧/操作認可を区別する。GitHub CIには未接続であり、Issue8/9全体は完了扱いにしていない。

## 施設アクセス・challenge段階

API Issue9のquery層とIssue10のchallenge基盤を追加。外部から生成/JSON decodeできないVerifiedSubjectと、各SQLで施設/active membership/roleを再検査するFacilityStoreを実装した。認証済subjectのproducerはまだなく、業務HTTPは公開していない。

PostgreSQL challenge tableと原子的consumeを追加し、CSPRNG nonceとSHA-256のbrowser-flow binding、RP/origin/purpose、DB時刻での期限を管理する。16並行consumeの1成功、row lock待ちで期限超過の拒否を実DB回帰で確認。host Swift38tests、SQL拒否29件、Python26testsが成功。詳細と独立review結果はsauna-api/docs/LOCAL_IDENTITY.md / LOCAL_VALIDATION.mdに記録する。

ローカル仮想認証器鍵/専用token生成はユーザー承認済み。Sauna本体での追加生成はメモリ上のnonceとflow bindingで、Passkey credentialやログインsessionはまだ生成していない。署名/UV・session/Workspace・公開認証API・remote CIは未実装/未検証の範囲として残る。

最終sourceのApple container/Linux release build/testも成功（24成功、secretを渡さないDB14件はskip）。API新imageの再起動後health/versionを実HTTPで確認した。上流WebAuthn評価はbeta1で38、修正済main固定SHAで63tests成功し、互換修正が既に本家にあるため重複forkなし。Sauna依存へは未追加。

## blindlog-api参照の固定

user指定blindlog-api@82a13ed73fff44984e8954781d669cf8320883eaのPackage/Sources/lockを基準にした構成・依存/fork評価をsauna-api/docs/BLINDLOG_REFERENCE.mdへ記録。自前production6targetsへ同じ厳格compiler設定を適用し、public/direct importsを修正。host build/実DB38testsとsubject境界scriptが成功、独立Review/Securityのblocking指摘なし。依存は無差別に追加せず、認証/型付きSQL/OTel等の採用評価の起点とする。ADR0010とWiki索引へ反映済み。今回もlocal-only。
