以下是您所提供的敘述轉換成 Markdown 格式：

```markdown
# Celery 安裝與啟動指南

## 1. 安裝 Celery

首先，在您的虛擬環境中安裝 Celery：

```bash
pip install celery
```

## 2. 啟用 Celery Worker 和 Beat

要開始執行 Celery 並處理任務，您需要運行 Celery Worker 和 Celery Beat（如果使用定時任務）。

### 啟動 Celery Worker

在您的終端機中，運行以下命令來啟動 Celery Worker：

```bash
celery -A backend worker --loglevel=info
```

- `-A backend` 指向您的 Celery 應用（`backend` 應該是您的 Django 專案名稱）。
- `--loglevel=info` 會顯示有關任務處理的詳細日誌。

### 啟動 Celery Beat（可選，對於定時任務）

如果您正在使用定時任務（例如每分鐘發送郵件），則需要啟動 Celery Beat 來調度這些任務：

在`~/cafeMate_backend/backend`
```bash
celery -A backend beat --loglevel=info
```

- `beat` 會根據您在 `celery.py` 中定義的調度，觸發定時任務。

## 3. 監控與除錯

要查看任務和 Worker 的狀態，您可以使用以下 Celery 命令：

在`~/cafeMate_backend/backend`
```bash
celery -A backend status
```

要檢查和除錯任務，您可以使用 Celery 的內建日誌功能，並將日誌級別設為 `debug`，以便獲取更多詳細輸出：

在`~/cafeMate_backend/backend`
```bash
celery -A backend worker --loglevel=debug
```
```