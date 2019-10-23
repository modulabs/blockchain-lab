# Currency Rate 관련된 표기법

- 기본적으로 외환 거래와 똑같은 표기법을 쓰는 것을 원칙으로 합니다.

    - 예) 'btc/krw', 'eth/btc'
    
- 이와 일관적으로, 환율이 아니라 개별 암호화폐/통화를 표시할 때는 'krw', 'btc'와 같이 소문자로 표시하는 것을 원칙으로 합니다.
단, logging등에 표시할 경우, 문서 등에는 Readbility를 위해서 'BTC'로 표기할 수 있습니다.
    
- 'btc/krw'의 경우 KRW을 기반으로 BTC를 사는 것을 의미합니다. 여기서 KRW의 위치에 해당하는 통화를 Base currency라고 부르고, 
BTC의 위치에 해당하는 통화를 Quote/Counter currency라고 부릅니다. 

    - 예) BTC의 가격이 한화를 1800만원인 경우, 'btc/krw' 값은 18,000,000 입니다.
    - 예) BTC 1개로 10개의 ETH를 살 수 있는 경우, 'eth/btc' 값은 0.1이 됩니다.

- 거래소마다 currency rate의 표기법이 다른 경우가 있는데, code에서 parameter로 주고 받을 때는 
'btc/krw'와 같이 표시하고 각 거래소에 관련된 method 내부에서 convert해서 사용하도록 합니다.

## 거래소에 따른 Currency Rate 표기법

### Poloniex

- 'eth/btc'를 'BTC_ETH'로 표기합니다.

### Cex

- 'eth/btc'를 'ETH:BTC'로 표기합니다.


## 많이 사용되는 Currency 목록

- BTC, XBT : 비트코인 (bitmex, kraken에 xbt로 상장되어 있음)
- ETH : 이더리움 
- BCH, BCC : 비트코인 캐쉬 (binance에 BCC로 상장되어 있음)
- XRP : 리플
- BTG : 비트코인 골드
- ETC : 이더리움 클래식
- USDT : Tether라고 해서 USD reserve로 가치가 backed되는 가상화폐, 단 USD reserve를 독립적인 기관으로부터 감사를 받지 않아서 scam이라는 의혹이 있음
- XMR : 모네로
- LTC : 라이트코인
