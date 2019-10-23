# CARBI

암호화폐 차익거래 봇

## 사용 환경

Developed under python 2.7

## 환경 설정

1. use virtualenv to make .venv folder under this project root

	$ virtualenv .venv
	$ source .venv/bin/activate

2. upgrade pip if needed

	$ pip install --upgrade pip

3. install all pip packages

	$ pip install -r requirments.txt

4. prepare configuration under conf/coinone.json (access_token, secret_key)

5. start main.py

	$ python main.py

5. when terminate

	$ deactivate
