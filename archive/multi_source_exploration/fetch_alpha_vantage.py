"""
Alpha Vantage数据源实现（备用数据源）

注意：免费版限制为每分钟5次调用，每天500次
"""

import requests
import logging
import os
import time
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from core.models import StockData
from core.format_utils import normalize_ticker, get_currency_from_ticker
from core.schemas.validation_rules import ValidationRules

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
BASE_URL = 'https://www.alphavantage.co/query'

# 速率限制
RATE_LIMIT_CALLS = 5  # 每分钟调用次数
RATE_LIMIT_PERIOD = 60  # 秒
_last_call_times = []


def _check_rate_limit():
    """检查并控制API调用速率"""
    global _last_call_times
    
    now = time.time()
    
    # 清理超过1分钟的记录
    _last_call_times = [t for t in _last_call_times if now - t < RATE_LIMIT_PERIOD]
    
    # 如果达到限制，等待
    if len(_last_call_times) >= RATE_LIMIT_CALLS:
        wait_time = RATE_LIMIT_PERIOD - (now - _last_call_times[0]) + 1
        logger.warning(f"达到速率限制，等待 {wait_time:.0f} 秒...")
        time.sleep(wait_time)
        _last_call_times = []
    
    _last_call_times.append(now)


def fetch_stock_data(ticker: str, date: Optional[str] = None) -> Optional[StockData]:
    """
    从Alpha Vantage获取股票数据并计算PEG
    
    Args:
        ticker: 股票代码
        date: 数据日期（默认为最新）
    
    Returns:
        StockData对象，失败返回None
    """
    try:
        # 标准化股票代码
        ticker = normalize_ticker(ticker)
        logger.info(f"[AlphaVantage] 正在获取 {ticker} 的数据...")
        
        # 检查API Key
        if not API_KEY or API_KEY == 'demo':
            logger.warning(f"{ticker}: 未配置Alpha Vantage API Key，使用demo密钥（功能受限）")
        
        # 速率控制
        _check_rate_limit()
        
        # 1. 获取实时报价
        quote_params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker.replace('.HK', ''),  # Alpha Vantage不支持.HK后缀
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=quote_params, timeout=10)
        response.raise_for_status()
        quote_data = response.json()
        
        if 'Global Quote' not in quote_data or not quote_data['Global Quote']:
            logger.warning(f"{ticker}: 无法从Alpha Vantage获取报价数据")
            return None
        
        price = float(quote_data['Global Quote'].get('05. price', 0))
        if price <= 0:
            logger.warning(f"{ticker}: 价格数据无效")
            return None
        
        # 2. 获取公司概览（包含PE等指标）
        _check_rate_limit()
        
        overview_params = {
            'function': 'OVERVIEW',
            'symbol': ticker.replace('.HK', ''),
            'apikey': API_KEY
        }
        
        response = requests.get(BASE_URL, params=overview_params, timeout=10)
        response.raise_for_status()
        overview = response.json()
        
        if not overview or 'Symbol' not in overview:
            logger.warning(f"{ticker}: 无法获取公司概览数据")
            return None
        
        # 提取财务数据
        try:
            # TTM EPS和PE
            eps = float(overview.get('EPS', 0))
            pe = float(overview.get('PERatio', 0))
            
            if pe <= 0 and eps > 0:
                pe = price / eps
            
            # 获取净利润（从季度盈利）
            _check_rate_limit()
            
            earnings_params = {
                'function': 'EARNINGS',
                'symbol': ticker.replace('.HK', ''),
                'apikey': API_KEY
            }
            
            response = requests.get(BASE_URL, params=earnings_params, timeout=10)
            response.raise_for_status()
            earnings = response.json()
            
            # 计算TTM利润和增长率
            ttm_profit = 0
            growth_rate = 0.0
            
            if 'quarterlyEarnings' in earnings and len(earnings['quarterlyEarnings']) >= 4:
                quarterly = earnings['quarterlyEarnings']
                
                # 最近4季度
                recent_4q = sum(float(q.get('reportedEPS', 0)) for q in quarterly[:4])
                
                # 去年同期4季度
                if len(quarterly) >= 8:
                    prev_4q = sum(float(q.get('reportedEPS', 0)) for q in quarterly[4:8])
                    
                    if prev_4q != 0:
                        growth_rate = (recent_4q - prev_4q) / abs(prev_4q)
                
                # 估算净利润（EPS * shares）
                shares = float(overview.get('SharesOutstanding', 0))
                if shares > 0:
                    ttm_profit = recent_4q * shares * 1_000_000  # SharesOutstanding in millions
            else:
                logger.warning(f"{ticker}: 季度盈利数据不足")
                return None
            
            # 计算PEG
            if pe > 0 and growth_rate > 0:
                peg = pe / (growth_rate * 100)
            else:
                peg = 0.0
            
            # 数据验证
            should_reject, reject_reason = ValidationRules.should_reject_data(
                pe=pe,
                peg=peg if peg > 0 else 1.0,  # 避免PEG=0导致拒绝
                growth_rate=growth_rate,
                price=price,
                ticker=ticker
            )
            
            if should_reject:
                logger.error(f"{ticker}: Alpha Vantage数据被拒绝 - {reject_reason}")
                return None
            
            # 货币类型
            currency = get_currency_from_ticker(ticker)
            
            # 构建StockData
            stock_data = StockData(
                ticker=ticker,
                date=date or datetime.now().strftime('%Y-%m-%d'),
                price=price,
                market_cap=float(overview.get('MarketCapitalization', 0)) if overview.get('MarketCapitalization') else None,
                ttm_profit=ttm_profit,
                shares_outstanding=float(overview.get('SharesOutstanding', 0)) * 1_000_000 if overview.get('SharesOutstanding') else None,
                growth_rate=growth_rate,
                pe=pe,
                peg=peg,
                currency=currency,
                data_source='alpha_vantage',
                confidence='HIGH'
            )
            
            # 警告检查
            _, pe_warning = ValidationRules.validate_pe(pe, ticker)
            _, peg_warning = ValidationRules.validate_peg(peg, ticker) if peg > 0 else (True, None)
            _, growth_warning = ValidationRules.validate_growth_rate(growth_rate, ticker)
            
            if pe_warning or peg_warning or growth_warning:
                stock_data.confidence = 'MEDIUM'
                warnings = [w for w in [pe_warning, peg_warning, growth_warning] if w]
                stock_data.error_message = "; ".join(warnings)
            
            logger.info(f"{ticker}: Alpha Vantage数据获取成功 - PE={pe:.2f}, PEG={peg:.2f}")
            return stock_data
            
        except (KeyError, ValueError) as e:
            logger.error(f"{ticker}: 财务数据解析失败 - {e}")
            return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"{ticker}: Alpha Vantage API请求失败 - {e}")
        return None
    
    except Exception as e:
        logger.error(f"{ticker}: 数据获取失败 - {e}")
        return None


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n=== 测试Alpha Vantage数据源 ===")
    print("注意：需要设置ALPHA_VANTAGE_API_KEY环境变量")
    print("获取免费API Key: https://www.alphavantage.co/support/#api-key\n")
    
    # 测试IBM（Alpha Vantage的示例股票）
    data = fetch_stock_data('IBM')
    if data:
        print(f"✓ 价格: ${data.price:.2f}")
        print(f"✓ PE: {data.pe:.2f}")
        print(f"✓ PEG: {data.peg:.2f}")
        print(f"✓ 增长率: {data.growth_rate:.1%}")
        print(f"✓ 数据源: {data.data_source}")
    else:
        print("✗ 数据获取失败")

