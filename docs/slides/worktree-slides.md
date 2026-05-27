# Gitflow + Worktrees — Quy trình song song, an toàn hơn cho dev và AI coding

---

## Vì sao cần thay đổi

- Branch local lâu ngày → rủi ro mất code khi máy hỏng.
- Làm xong mới push → team khó theo dõi, khó review sớm.
- Một folder local → chuyển task phải stash/checkout liên tục, dễ sai.

---

## Gitflow recap

- `main`: lịch sử release chính thức.
- `develop`: branch tích hợp feature.
- `feature/*`: tạo từ `develop`, merge lại khi xong.
- `release/*` và `hotfix/*`: tách riêng giai đoạn chuẩn bị release và sửa lỗi khẩn.

---

## Worktree recap

- Một repo Git → nhiều working tree, mỗi cái gắn một branch.
- Mỗi worktree có bộ file riêng → tách task local rất sạch.
- Phù hợp cho feature song song, review branch người khác, AI coding đa session.

---

## Gitflow và worktree bổ sung cho nhau

| Chủ đề | Gitflow | Worktree |
|---|---|---|
| Mục tiêu | Quản lý vòng đời branch và release | Quản lý nhiều workspace local cùng lúc |
| Đơn vị | `feature/*`, `release/*`, `hotfix/*` | Một thư mục local cho mỗi branch |
| Giá trị chính | Kỷ luật branch của team | Giảm context switching |
| Với AI | Branch/PR rõ ràng | Cô lập từng agent hoặc từng task |

---

## Quy ước đặt tên

- Branch: `feature/ABC-123-login`, `hotfix/ABC-999-null-check`
- Worktree folder: `ABC-123-login`, `ABC-999-null-check`
- Không thêm tên project vào folder worktree — repo path đã đủ ngữ cảnh.

---

## Bắt đầu task theo cách mới

Tạo branch trên origin trước, rồi mới tạo worktree:

```
cd ~/projects/myapp
git checkout develop && git pull --ff-only
git checkout -b feature/ABC-123-login
git push -u origin feature/ABC-123-login
git worktree add ../ABC-123-login feature/ABC-123-login
cd ../ABC-123-login
```

Lý do: branch lên origin ngay → backup cloud + cộng tác sớm. Worktree sau → workspace riêng.

---

## Vì sao phải tạo branch trên origin ngay

- Code có bản sao trên cloud, không chỉ nằm local.
- Team lead, reviewer, CI nhìn thấy branch sớm.
- Publish sớm khác merge sớm — chỉ là backup và theo dõi tiến độ.

---

## Cấu trúc thư mục

```
proj-api/                          ← repo chính (giữ sạch)
proj-api-worktrees/                ← tất cả worktrees (phẳng)
├── proj-111-adjust-text/          ← nhánh feature/proj-111-...
│   ├── .ai/
│   ├── src/
│   └── .env
├── proj-222-login-google/         ← nhánh feature/proj-222-...
├── proj-333-update-button/        ← nhánh hotfix/proj-333-...
└── proj-444-login-issue/          ← nhánh hotfix/proj-444-...
```

- Folder worktree: short name, không prefix.
- Git branch: format đầy đủ `type/key-summary`.
- Main repo luôn sạch — mọi thao tác trong worktree.

---

## Workflow hằng ngày

- Repo chính giữ ở `develop` làm mốc ổn định.
- Mỗi task: một branch origin + một worktree local.
- Code, test, diff, commit, push đều trong worktree tương ứng.

---

## Review thay đổi

Review trong chính worktree của task — không cần chuyển branch:

```
git status
git diff
git add .
git commit -m "ABC-123: implement login"
git push
```

---

## Review branch của người khác

Dùng worktree riêng — không ảnh hưởng task đang làm:

```
cd ~/projects/myapp
git fetch origin
git worktree add ../ABC-456-review origin/feature/ABC-456-api-cleanup
cd ../ABC-456-review
```

Build, test, fix trên branch review mà workspace hiện tại vẫn nguyên.

---

## Hotfix scenario

Xử lý lỗi production trong khi vẫn giữ feature đang làm:

```
cd ~/projects/myapp
git checkout main && git pull --ff-only
git checkout -b hotfix/ABC-999-null-check
git push -u origin hotfix/ABC-999-null-check
git worktree add ../ABC-999-null-check hotfix/ABC-999-null-check
cd ../ABC-999-null-check
```

---

## Vì sao phù hợp với AI workflow

- Mỗi agent/task: branch riêng + workspace riêng → tránh ghi đè.
- Branch lên origin sớm → output AI được backup hằng ngày.
- Review, rollback, theo dõi tiến độ AI rõ ràng hơn.

---

## Sơ đồ workflow AI

Con người điều phối → tạo branch + worktree → agent thực thi → commit + push hằng ngày → review từng branch → merge vào develop

- Người điều phối: xác định scope, chia task rõ ràng.
- Agent 1 (API/Backend): branch `feature/ABC-123-api`, worktree `../ABC-123-api`
- Agent 2 (UI/Frontend): branch `feature/ABC-456-ui`, worktree `../ABC-456-ui`
- Agent 3 (Tests/Refactor): branch `feature/ABC-789-tests`, worktree `../ABC-789-tests`
- Mỗi agent commit nhỏ + push hằng ngày.
- Review từng branch độc lập bằng `git diff` + test.
- Merge từng branch một vào `develop`.

---

## Chạy nhiều AI agents song song

```
cd ~/projects/myapp
git checkout develop && git pull --ff-only

git checkout -b feature/ABC-123-api
git push -u origin feature/ABC-123-api
git worktree add ../ABC-123-api feature/ABC-123-api

git checkout develop
git checkout -b feature/ABC-456-ui
git push -u origin feature/ABC-456-ui
git worktree add ../ABC-456-ui feature/ABC-456-ui
```

- Mỗi agent: branch riêng, worktree riêng, push định kỳ.
- Chia theo boundary: backend, UI, tests → giảm overlap file.

---

## Quy trình khi chạy nhiều AI agents

1. Chốt scope và acceptance criteria trước.
2. Tạo branch trên origin ngay cho từng task.
3. Tạo worktree riêng cho từng agent.
4. Commit nhỏ và push hằng ngày để backup.
5. Review từng branch rồi merge từng cái một.

---

## Test API và UI ở 2 worktree riêng?

- Unit test / test độc lập → test trong từng worktree.
- Integration test → cần branch tích hợp tạm:

```
cd ~/projects/myapp
git worktree add ../ABC-900-integration -b integration/ABC-900 develop
cd ../ABC-900-integration
git merge feature/ABC-123-api
git merge feature/ABC-456-ui
# chạy integration test full-stack ở đây
```

---

## Team rules

- Mỗi task: tạo branch trên `origin` ngay khi bắt đầu.
- Mỗi task: một worktree riêng local.
- Commit nhỏ, push hằng ngày để backup cloud.
- Không sửa trực tiếp trên `main` hoặc `develop`.
- Mọi branch phải review trước khi merge.

---

## Cleanup

```
cd ~/projects/myapp
git worktree list
git worktree remove ../ABC-123-login
git branch -d feature/ABC-123-login
```

- Sau merge: remove worktree, xóa local branch.
- Giữ remote branch thêm thời gian ngắn nếu cần audit.

---

## Kết luận

- Gitflow → kỷ luật branch và release.
- Worktree → làm việc local song song hiệu quả.
- Branch trên origin ngay + push hằng ngày → code an toàn, tiến độ quan sát được.
- Kết hợp cả ba → giảm rủi ro, review dễ hơn, dùng AI có kiểm soát.
