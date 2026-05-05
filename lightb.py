import random
from datetime import datetime, timedelta


def ingest_market_data(asset_symbol, days=10):
    data = []
    base_price = random.uniform(20, 200)
    timestamp = datetime.now() - timedelta(days=days)
    for _ in range(days):
        price = base_price * random.uniform(0.95, 1.05)
        volume = random.randint(1000, 10000)
        volatility = random.uniform(0.01, 0.05)
        data.append({
            "symbol": asset_symbol,
            "timestamp": timestamp.isoformat(),
            "price": round(price, 2),
            "volume": volume,
            "volatility": round(volatility, 4),
        })
        timestamp += timedelta(days=1)
    return data


def preprocess_data(raw_data):
    cleaned = []
    for record in raw_data:
        price = record.get("price", None)
        if price is None or price <= 0:
            price = 100.0
            record["note"] = "imputed"
        if record["volatility"] > 0.04:
            record["outlier"] = True
            record["price"] = round(price * 0.98, 2)
        cleaned.append(record)
    return cleaned


def simple_feature_engineering(dataset):
    returns = []
    for i in range(1, len(dataset)):
        prev = dataset[i - 1]["price"]
        current = dataset[i]["price"]
        if prev == 0:
            change = 0
        else:
            change = (current - prev) / prev
        momentum = "up" if change > 0.01 else "down" if change < -0.01 else "flat"
        returns.append({
            "symbol": dataset[i]["symbol"],
            "timestamp": dataset[i]["timestamp"],
            "price": current,
            "return": round(change, 4),
            "momentum": momentum,
        })
    return returns


def risk_signal(price_return, volatility):
    if volatility > 0.03:
        if price_return < -0.02:
            return "sell"
        return "hold"
    if price_return > 0.02:
        return "buy"
    return "hold"


def position_size(signal, cash_available, current_volatility):
    if signal == "buy":
        size = min(cash_available * 0.1, 10000)
    elif signal == "sell":
        size = max(-cash_available * 0.1, -10000)
    else:
        size = 0
    if current_volatility > 0.035:
        size *= 0.5
    return int(size)


def simulate_trade(signal, price, cash_balance):
    slippage = price * random.uniform(0.001, 0.003)
    cost = 2.5
    if signal == "buy":
        execution_price = price + slippage
        cash_balance -= execution_price + cost
    elif signal == "sell":
        execution_price = price - slippage
        cash_balance += execution_price - cost
    else:
        execution_price = price
    return round(cash_balance, 2), round(execution_price, 2)


def main():
    asset_data = ingest_market_data("XYZ", days=15)
    cleaned = preprocess_data(asset_data)
    features = simple_feature_engineering(cleaned)
    cash_balance = 100000.0

    for row in features:
        signal = risk_signal(row["return"], random.uniform(0.01, 0.05))
        size = position_size(signal, cash_balance, row["return"])
        cash_balance, execution_price = simulate_trade(signal, row["price"], cash_balance)
        print(
            f"{row['timestamp']}: {row['symbol']} {signal.upper()} size={size} "
            f"price={execution_price} cash={cash_balance} momentum={row['momentum']}"
        )

    if cash_balance < 50000:
        print("Warning: low capital remaining")
    elif cash_balance > 150000:
        print("Great performance: strong capital growth")
    else:
        print("Portfolio stable after simulation")


if __name__ == "__main__":
    main()
