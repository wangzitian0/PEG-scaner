from django.core.management.base import BaseCommand, CommandError
from backend.stock_research.models import Stock, KLineData, CompanyInfo, CompanyValuation, FinancialIndicators, EarningData
import yfinance as yf
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fetches stock data for a given symbol and saves it to the database'

    def add_arguments(self, parser):
        parser.add_argument('symbols', nargs='+', type=str, help='Stock symbols to fetch data for')

    def handle(self, *args, **options):
        for symbol in options['symbols']:
            self.stdout.write(self.style.SUCCESS(f'Fetching data for {symbol}...'))
            try:
                # Get or create the Stock object
                stock, created = Stock.objects.get_or_create(symbol=symbol)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new stock: {symbol}'))

                ticker = yf.Ticker(symbol)

                # --- Fetch and save Company Info ---
                info = ticker.info
                company_info, created = CompanyInfo.objects.update_or_create(
                    symbol=symbol,
                    defaults={
                        'description': info.get('longBusinessSummary'),
                        'sector': info.get('sector'),
                        'industry': info.get('industry'),
                    }
                )
                stock.company_info = company_info
                stock.name = info.get('longName')
                stock.exchange = info.get('exchange')
                stock.currency = info.get('currency')
                stock.save()
                self.stdout.write(self.style.SUCCESS(f'Updated company info for {symbol}'))

                # --- Fetch and save Company Valuation ---
                CompanyValuation.objects.update_or_create(
                    company=company_info,
                    defaults={
                        'ps_ratio': info.get('priceToSalesTrailing12Months'),
                        'pe_ratio': info.get('trailingPE'),
                        'pb_ratio': info.get('priceToBook'),
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Updated company valuation for {symbol}'))
                
                # --- Fetch and save Financial Indicators ---
                FinancialIndicators.objects.update_or_create(
                    company=company_info,
                    defaults={
                        'eps': info.get('trailingEps'),
                        'fcf': info.get('freeCashflow'),
                        'current_ratio': info.get('currentRatio'),
                        'roe': info.get('returnOnEquity'),
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Updated financial indicators for {symbol}'))

                # --- Fetch and save Earnings Data ---
                earnings = ticker.earnings_dates
                if earnings is not None:
                    for date, data in earnings.iterrows():
                        EarningData.objects.update_or_create(
                            company=company_info,
                            fiscal_date_end=date.date(),
                            defaults={
                                'reported_eps': data.get('Reported EPS'),
                                'estimated_eps': data.get('EPS Estimate'),
                            }
                        )
                    self.stdout.write(self.style.SUCCESS(f'Updated earnings data for {symbol}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No earnings data found for {symbol}'))
                
                # --- Fetch and print News ---
                news = ticker.news
                if news:
                    self.stdout.write(self.style.SUCCESS(f'News for {symbol}:'))
                    for item in news:
                        self.stdout.write(f"- {item['title']} ({item['publisher']})")
                else:
                    self.stdout.write(self.style.WARNING(f'No news found for {symbol}'))

                # --- Fetch and save K-line data ---
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7) # Fetch a bit more to ensure 5 trading days
                stock_data = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
                if not stock_data.empty:
                    for index, row in stock_data.iterrows():
                        KLineData.objects.update_or_create(
                            stock=stock,
                            timestamp=index,
                            defaults={
                                'open': row['Open'],
                                'high': row['High'],
                                'low': row['Low'],
                                'close': row['Close'],
                                'volume': row['Volume']
                            }
                        )
                    self.stdout.write(self.style.SUCCESS(f'Successfully saved K-line data for {symbol}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No K-line data found for {symbol}'))

            except Exception as e:
                raise CommandError(f'Error fetching or saving data for {symbol}: {e}')
