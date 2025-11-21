from django.core.management.base import BaseCommand, CommandError
from backend.stock_research.models import Stock, KLineData
import yfinance as yf
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fetches daily K-line data for a given stock symbol and saves it to the database'

    def add_arguments(self, parser):
        parser.add_argument('symbols', nargs='+', type=str, help='Stock symbols to fetch data for')

    def handle(self, *args, **options):
        for symbol in options['symbols']:
            self.stdout.write(self.style.SUCCESS(f'Fetching daily K-line for {symbol}...'))
            try:
                stock, created = Stock.objects.get_or_create(symbol=symbol)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new stock: {symbol}'))
                
                # Fetch data for the last 5 days
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
