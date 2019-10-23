# CARBI

암호화폐 차익거래 봇

## 설명

한국과 외국의 여러 거래소에서 여러 개의 코인의 orderbook을 보고, 그 사이에 이득을 볼 수 있는 기회를 찾아서 market order로 거래를 진행합니다.

지원하는 거래소는 현재 coinone, bitfinex, cex, korbit, binanace 을 지원합니다.

코인은 btc, eth, bch, xrp 를 지원합니다.

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
