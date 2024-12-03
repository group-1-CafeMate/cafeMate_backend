# cafeMate_backend

## Step1: 創建虛擬環境
`conda env create -f environment.yml`

## Step2: 安裝套件
```bash
cd cafeMate_backend/backend/
conda activate my_project_env
```

## 測api（推薦）

### Step1: 建立`./backend/.env`
如下
```bash
DEBUG=true
SECRET_KEY=e71f6d657f8b48b8b34c99d3f8a1d8a7e9a40e826d6f4dbb9f1b4502ac4db874
MYSQL_NAME=cafematedb
MYSQL_USER=root
MYSQL_PASSWORD=your_database_password
MYSQL_HOST=127.0.0.1
```
`SECRET_KEY`為自訂隨機生成的金鑰

### Step2: 建立mock data `cafe.json`
如下
```bash
[
    {
        "model": "cafeInfo.cafe",
        "pk": 1,
        "fields": {
            "name": "Fake Cafe 1",
            "legal": true,
            "grade": 5,
            "open_hour": "8:00-16:00",
            "open_now": true,
            "distance": 2.5,
            "quiet": true,
            "time_unlimit": true,
            "socket": true,
            "pets_allowed": false,
            "wiFi": true,
            "info": "This is a sample cafe.",
            "comment": "Very peaceful place.",
            "ig_link": "http://instagram.com/fakecafe1",
            "ig_post_cnt": 20,
            "fb_link": "http://facebook.com/fakecafe1"
        }
    },
    {
        "model": "cafeInfo.cafe",
        "pk": 2,
        "fields": {
            "name": "Fake Cafe 2",
            "legal": true,
            "grade": 4,
            "open_hour": "10:00-16:00",
            "open_now": true,
            "distance": 1.5,
            "quiet": true,
            "time_unlimit": true,
            "socket": true,
            "pets_allowed": true,
            "wiFi": true,
            "info": "This is a noisy cafe.",
            "comment": "Very noisy place.",
            "ig_link": "http://instagram.com/fakecafe1",
            "ig_post_cnt": 120,
            "fb_link": "http://facebook.com/fakecafe1"
        }
    }
]
```

### Step3: 載入mockdata進本地端資料庫
```bash
python manage.py loaddata path/to/cafe.json
```

### Step4: 啟用server
```bash
python manage.py runserver 
```
