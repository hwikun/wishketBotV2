# wishketBotV2

위시켓 크롤러 업데이트 버전 with lambda by bs4

### 사용방법

```bash
# virtualenv + virtualenvwrapper 설치 후
# 프로젝트 폴더에서 가상환경 생성
$ mkvirtualenv {가상환경 이름}
$ workon {가상환경 이름}

# 필요 패키지 설치
$ pip install {패키지 이름}

# requirements.txt 생성하기
$ pip freeze > requirements.txt

# lambda 계층에 넣어줄 패키지 설치경로 생성
$ mkdir -p ./layer/python/lib/python3.11/site-packages

# 패키지 설치
$ pip install -r requirements.txt --target ./layer/bs4/python/lib/python3.11/site-packages
```

이후 python 폴더를 .zip로 압축 후 lambda console 에서 계층 생성 후 추가.

main.py 에서 bucket_name과 bucket_key, telegram_url에 알맞게 값 바꾸기

lambda에 올릴 때는 맨 아래 두 줄 지우고 deploy 후 test.

---
