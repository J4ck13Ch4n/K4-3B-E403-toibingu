"""One real API call; uses .env without printing credentials."""
import sys
import app

try:
    checks, response_id = app.evaluate([{'role': 'user', 'text': 'Temperature là độ sáng tạo. Mình chưa hiểu cơ chế.'}])
    print('Response ID:', response_id)
    for check in checks:
        print(check['id'], check['status'])
except app.AppError as exc:
    print(str(exc).encode('ascii', 'backslashreplace').decode(), file=sys.stderr)
    sys.exit(1)
