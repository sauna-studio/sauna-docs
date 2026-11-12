# ADR-0025: Google Workspace連携の認可と資格情報

Status: Proposed / 2026-11-13

## Context

[ADR-0002](0002-identity-and-workspace.md) はPasskey認証とGoogle Workspace連携の境界を定めた。[W01](https://github.com/sauna-studio/sauna-automation/issues/2) では、連携ごとのAPI、OAuthスコープ、Google上の実行主体と資格情報の扱いを決める。Workspaceは所属情報と業務データの派生ビューに使う。Sauna APIとPostgreSQLが予約・決済・シフトの正本で、施設権限はSauna APIのmembershipで判定する。

## Decision

### 連携別の認可

スコープは機能を有効にする際に個別に付与する。下表のスコープ名は `https://www.googleapis.com/auth/` に続く接尾辞。OAuthスコープに加え、各APIの管理者権限・対象リソースのACLと、アプリ内の対象許可リストが必要になる。

| 用途・操作 | 最小スコープ | 認可主体・対象 |
| --- | --- | --- |
| Chatの同期応答 | なし | Google Chatからの受信リクエストを、構成した方式の署名・発行元・サービスID・audience・有効期限で検証し、応答本文を返す。送信者とスペースをSauna側で認可する。 |
| Chatの非同期通知 `spaces.messages.create` | `chat.bot` | 専用Chatアプリのサービスアカウント。アプリが参加し、設定で許可したスペースへの通知のみ。ユーザーとしての投稿、メッセージ履歴の読み取り、管理者承認を伴う `chat.app.*` は初期対象外。 |
| Calendarの投影先作成と予約・シフト投影 `calendars.insert`・`events.insert/get/update/delete` | `calendar.app.created` | 連携専用のWorkspaceユーザーがOAuthに同意し、アプリが作成した専用のセカンダリカレンダーへ反映する。外部カレンダーへ反映する要件が出た場合は、所有者専用の `calendar.events.owned` を含め、対象ACLとスコープを再評価する。 |
| Directoryの社員確認 `users.get` | `admin.directory.user.readonly` | 読み取りに必要な権限だけを持つ委任管理者のユーザーOAuth。既知のリンク対象を `admin_view` で個別照会し、`id,customerId,suspended,archived` に絞る。初回に識別子の対応付けが必要な場合のみ、検証済みIDトークンで `email_verified=true` のメールを照会に使う。組織の全件取得を既定にしない。 |
| Groupsの所属確認 `members.hasMember` | `admin.directory.group.member.readonly` | 照会に必要な権限だけを持つ委任管理者のユーザーOAuth。許可した組織内Group IDとDirectoryユーザーIDの組だけ照会する。同一ドメイン内のネストのみ対象。 |
| Driveの運用資料 `files.get` | `drive.file` | 権限を持つWorkspaceユーザーが当該アプリで選択したファイルのみ。Drive全体の列挙・共有変更・本文同期は初期対象外。 |

操作別の根拠は [Chat認可](https://developers.google.com/workspace/chat/authenticate-authorize)、[Chat要求の検証](https://developers.google.com/workspace/chat/verify-requests-from-chat)、[Calendarスコープ](https://developers.google.com/workspace/calendar/api/auth)、[Calendar作成](https://developers.google.com/workspace/calendar/api/v3/reference/calendars/insert)、[Calendar Events](https://developers.google.com/workspace/calendar/api/v3/reference/events)、[Directory users.get](https://developers.google.com/workspace/admin/directory/reference/rest/v1/users/get)、[Directory members.hasMember](https://developers.google.com/workspace/admin/directory/reference/rest/v1/members/hasMember)、[Driveスコープ](https://developers.google.com/workspace/drive/api/guides/api-specific-auth) を参照。

- 社員がGoogleアカウントを紐付けるときは、既存Passkeyセッションに紐付く再認証済みの短寿命・単回リンクintentから認可コードフローを開始する。コールバックの `state` をリンクintentと照合し、PKCEを使ってコードを交換する。`openid email` で受け取るIDトークンの署名・`iss`・`aud`・期限・`nonce` を検証する。署名済み `hd` が許可したドメインと一致し、Directoryの `customerId` が対象テナントに一致する有効なユーザーと確認できた場合に、`iss/sub` と検証したDirectory IDを別々に紐付ける。既存リンクとの `iss/sub` またはDirectory IDの衝突を拒否する。再確認は保存したDirectory IDを使い、メール変更や再割り当てでリンクを変更しない。メールやドメインだけで本人確認・施設権限付与を行わない。GoogleのIDトークンはSaunaセッションの発行に使わない。[Google OpenID Connect](https://developers.google.com/identity/openid-connect/openid-connect)
- スコープは閲覧可能な主体・資源の粒度まで縮められるとは限らない。`admin.directory.user.readonly` は、委任管理者の持つ読み取り権限で対象となるユーザーに作用する。個別照会やfields制限はアプリの制約として実装し、管理者権限が足りない場合は確認済みと扱わない。所属・停止・退職を再検証し、権限失効と監査に反映する。Google側のグループはSauna側の施設ロールを自動付与しない。
- Calendarはoutboxと予約・シフトIDに対応する安定したevent IDで一方向に投影する。再試行でイベントを重複作成しない。連携には運用に必要な情報のみを渡し、Google側の変更で在庫・シフトを更新しない。Chat通知も許可スペースを絞り、利用者の個人情報や決済情報を含めない。

### SDKとRESTの境界

| 対象 | 方式 |
| --- | --- |
| Cloud Storage | Google公式Swift SDKの `swift-google-cloud-storage` が存在。必要な場合だけ、対象操作と対応バージョンを検証して採用する。 |
| Cloud Tasks・Secret Manager | Google公式Swift SDKの生成ツリーに [Cloud Tasks v2](https://github.com/googleapis/google-cloud-swift/tree/main/generated/swift-google-cloud-tasks-v2) と [Secret Manager v1](https://github.com/googleapis/google-cloud-swift/tree/main/generated/swift-google-cloud-secretmanager-v1) がある。採用時に公開パッケージと対象操作を確認する。 |
| Chat・Calendar・Directory・Groups・Drive | Workspace RESTを対象に、操作別に型付きアダプターとテスト用実装を用意する。Google Cloud Swift SDKの対応サービスからWorkspaceの対応や認可を推定しない。 |

[Google Cloud Swiftパッケージ一覧](https://github.com/googleapis/google-cloud-swift/tree/main/pkgs)、[Google Cloud Swiftの生成ツリー](https://github.com/googleapis/google-cloud-swift/tree/main/generated)、[Google Workspace API](https://developers.google.com/workspace)。

外部連携はOAuthとHTTP呼び出しを分離し、固定したAPIの宛先・必要項目・対象IDをアダプターで検証する。ページングを使う操作は境界・件数を制限し、429/一時障害は上限付き再試行で扱う。403や失効は運用者へ通知し、権限を広げて自動復旧しない。

### 資格情報と承認の境界

- Domain-wide delegation（DWD）は既定で無効。ユーザー同意によるOAuthと、Cloud実行サービスのサービスアカウントは分離する。DWDが必要になった場合は、組織管理者が対象テナント・主体・スコープ・必要性・失効手順を承認してから別ADRで判断する。対象のアプリ内許可リストはDWD自体の代理範囲を狭めない。管理者権限の拡大も別途承認する。[DWDを避けるためのGoogle IAM指針](https://docs.cloud.google.com/iam/docs/best-practices-service-accounts#avoid_using_domain-wide_delegation)
- クラウドの実行サービスは専用サービスアカウントの鍵なし実行IDを使う。Chatの `chat.bot` についてはデプロイ設計時に必要スコープを持つ短寿命トークンの発行方法を検証する。Cloud Runの実行IDがあるだけでWorkspace権限を持つとは扱わない。サービスアカウントJSON鍵の発行・保管は採用しない。[Cloud RunサービスID](https://docs.cloud.google.com/run/docs/securing/service-identity)、[Google IAMの鍵管理指針](https://docs.cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys)
- 長期実行が必要な連携だけでrefresh tokenを受け取り、環境・連携・認可主体ごとに分けてサーバー側の承認済みSecret Managerに暗号化保管する。OAuthクライアントシークレットも同じ管理境界に置く。アクセス権を連携ワーカーに絞り、access tokenは必要時に更新して短期利用する。認可解除・失効時は連携を停止し、保管トークンを削除して再同意を要求する。トークンや秘密鍵をGit、CI、クライアント、ログ、テレメトリへ渡さない。[Google OAuth 2.0ポリシー](https://developers.google.com/identity/protocols/oauth2/policies)
- ローカル既定は連携無効。承認前は合成データとテスト用アダプターだけを使う。実API検証は、承認された開発テナント・OAuthクライアント・認可主体・対象資源が決まってから機能別に実施する。鍵・トークンの作成、権限付与、API有効化はこのADRの範囲外。

## Alternatives and consequences

DWDで管理者を一括代理する方式は、対象ユーザーが広く失効管理の影響も大きいため初期採用しない。各機能の認可を分離するため、ユーザーOAuthの同意・失効への対応と、管理者権限や各ACLが変わったときの運用手順が必要になる。開発テナントでの実認可、SDKの採用バージョン、権限とAPI呼び出しの検証は各実装Issueに残す。
