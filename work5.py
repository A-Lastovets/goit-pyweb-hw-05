import asyncio
import platform
import aiohttp
from datetime import datetime, timedelta

class ExchangeError(Exception):
    pass

class CurrencyRate:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    def __init__(self, days: int):
        self.days = days

    async def rates_for_date(self, session: aiohttp.ClientSession, date: str) -> dict:
        url = f"{self.BASE_URL}{date}"
        async with session.get(url) as response:
            if response.status != 200:
                raise ExchangeError(f"Failed to fetch data for {date}")
            return await response.json()

    async def get_rates(self) -> list:
        results = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.days):
                date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
                tasks.append(self.rates_for_date(session, date))
            results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

def get_number_days() -> int:
    while True:
        try:
            days = int(input("Enter the number of past days to fetch the rates for (max 10 days): "))
            if 1 <= days <= 10:
                return days
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
                print("Invalid input. Please enter a valid number.")

def print_rates(rates):
    for rate in rates:
        if isinstance(rate, ExchangeError):
            print(f"Error: {rate}")
            continue
        date = rate.get("date")
        exchange_rates = rate.get("exchangeRate", [])
        usd_rate = next((currency for currency in exchange_rates if currency.get("currency") == "USD"), None)
        eur_rate = next((currency for currency in exchange_rates if currency.get("currency") == "EUR"), None)
        print(f"Date: {date}")
        if usd_rate:
            print(f"USD: Buy - {usd_rate.get('purchaseRateNB')}, Sell - {usd_rate.get('saleRateNB')}")
        if eur_rate:
            print(f"EUR: Buy - {eur_rate.get('purchaseRateNB')}, Sell - {eur_rate.get('saleRateNB')}\n")


async def main():
    days = get_number_days()
    fetcher = CurrencyRate(days)
    rates = await fetcher.get_rates()
    print_rates(rates)

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
