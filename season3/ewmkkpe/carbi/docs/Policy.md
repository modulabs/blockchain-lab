# Exchange Policy

## Order policy

## Order Policy Configuration

```
{
    "btc/krw": { # equity_pair name
        # 거래소에 따라서 혹은 equity_pair에 따라서 price, volume, nominal pair 가 전부 없거나 일부가 존재하지 않을 수 있다.
        # 적용할 아무런 rule이 없다고 하더라도 "btc/krw" : {} 이런식으로 empty dictionary 를 넣어주는 것을 원칙으로 한다.
    
        "price": { 
            # 주문 시의 가격의 상한, 하한, 주문 단위를 나타낸다.
            
            "min": 100,
            "max": 10000,
            "step" 10
        },
        "volume": { 
            # 주문 시의 주문량의 상한, 하한, 주문 단위를 나타낸다.
            
            ...
        },
        "notional": {
            # Binance에만 있는 특이한 설정으로, 가격와 볼륨의 곱이 특정 값 이상이 되어야 하는 constraint이다.
            
            "min": 1000
            
            # 이 경우와 같이 min 만 존재하는 경우 나머지 constraint를 완전히 무시한다.
        }
    }
}
```
