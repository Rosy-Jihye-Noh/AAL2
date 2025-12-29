# 서버 시작 가이드

## 방법 1: 배치 파일 사용 (권장)

`server/start_server.bat` 파일을 더블클릭하여 실행하세요.

## 방법 2: 명령 프롬프트에서 실행

```bash
cd server
python main.py
```

## 방법 3: PowerShell에서 실행

```powershell
cd server
python main.py
```

## 서버 확인

서버가 시작되면 다음 메시지가 표시됩니다:
```
==================================================
Starting Flask Server on http://localhost:5000
==================================================
 * Running on http://127.0.0.1:5000
```

## 브라우저에서 접속

1. 브라우저를 열고 `http://127.0.0.1:5000` 또는 `http://localhost:5000` 접속
2. 또는 직접 IP 주소로 접속 (예: `http://YOUR_IP:5000`)

## 테스트 방법

서버가 실행 중일 때 다음 명령어로 테스트할 수 있습니다:

```bash
python server/test_server.py
```

## 문제 해결

### 포트 5000이 이미 사용 중인 경우

다른 Python 프로세스를 종료하세요:
```bash
taskkill /F /IM python.exe
```

또는 `server/main.py` 파일의 마지막 줄을 수정하여 다른 포트를 사용:
```python
app.run(port=5001, debug=True)  # 포트 변경
```







