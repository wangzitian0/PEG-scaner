"""
格式化工具函数
"""

from typing import Optional


# 公司名称映射表（格式：公司名<ticker.market>，注意小写）
COMPANY_NAMES = {
    # 美股七姐妹
    'AAPL': '苹果<aapl.us>',
    'MSFT': '微软<msft.us>',
    'GOOGL': '谷歌<googl.us>',
    'GOOG': '谷歌<goog.us>',
    'AMZN': '亚马逊<amzn.us>',
    'NVDA': '英伟达<nvda.us>',
    'META': 'Meta<meta.us>',
    'TSLA': '特斯拉<tsla.us>',
    
    # 港股七姐妹（保持原格式00700.hk）
    '700.HK': '腾讯<00700.hk>',
    '0700.HK': '腾讯<00700.hk>',
    '9988.HK': '阿里巴巴<09988.hk>',
    '09988.HK': '阿里巴巴<09988.hk>',
    '3690.HK': '美团<03690.hk>',
    '03690.HK': '美团<03690.hk>',
    '1810.HK': '小米<01810.hk>',
    '01810.HK': '小米<01810.hk>',
    '9618.HK': '京东<09618.hk>',
    '09618.HK': '京东<09618.hk>',
    '1211.HK': '比亚迪<01211.hk>',
    '01211.HK': '比亚迪<01211.hk>',
    '9999.HK': '网易<09999.hk>',
    '09999.HK': '网易<09999.hk>',
}


def format_profit(profit: float, currency: str = 'USD') -> str:
    """
    格式化利润显示
    
    Args:
        profit: 利润金额
        currency: 货币类型 (USD, HKD, CNY)
    
    Returns:
        格式化后的字符串，如 "$88.1B", "¥179.4B"
    """
    if profit == 0:
        return 'N/A'
    
    currency_symbol = '$' if currency == 'USD' else '¥'
    abs_profit = abs(profit)
    
    if abs_profit >= 1e9:
        return f"{currency_symbol}{profit/1e9:.1f}B"
    elif abs_profit >= 1e6:
        return f"{currency_symbol}{profit/1e6:.1f}M"
    elif abs_profit >= 1e3:
        return f"{currency_symbol}{profit/1e3:.1f}K"
    else:
        return f"{currency_symbol}{profit:,.0f}"


def format_ticker_name(ticker: str, include_name: bool = True) -> str:
    """
    格式化股票代码为显示名称
    
    Args:
        ticker: 股票代码
        include_name: 是否包含公司名
    
    Returns:
        格式化后的名称，如 "微软<msft.us>"（注意小写）
    """
    # 尝试从映射表获取
    if ticker.upper() in COMPANY_NAMES:
        return COMPANY_NAMES[ticker.upper()]
    
    # 自动生成格式（小写）
    if '.HK' in ticker.upper():
        # 港股：保留00700格式，小写后缀
        base = ticker.upper().replace('.HK', '')
        if include_name:
            return f"{base.zfill(5)}.hk"
        return f"{base.zfill(5)}.hk"
    elif '.' not in ticker:
        # 美股：小写
        ticker_lower = ticker.lower()
        if include_name:
            return f"{ticker_lower}.us"
        return f"{ticker_lower}.us"
    
    return ticker.lower()


def format_growth_rate(rate: float) -> str:
    """
    格式化增长率
    
    Args:
        rate: 增长率（小数，如0.218表示21.8%）
    
    Returns:
        格式化后的字符串，如 "21.8%"
    """
    if rate is None:
        return 'N/A'
    return f"{rate * 100:.1f}%"


def format_pe(pe: float) -> str:
    """
    格式化PE
    
    Args:
        pe: PE值
    
    Returns:
        格式化后的字符串
    """
    if pe is None or pe <= 0:
        return 'N/A'
    return f"{pe:.1f}"


def format_peg(peg: float) -> str:
    """
    格式化PEG
    
    Args:
        peg: PEG值
    
    Returns:
        格式化后的字符串
    """
    if peg is None:
        return 'N/A'
    
    # 突出显示低PEG（<1）
    formatted = f"{peg:.2f}"
    if peg < 1.0:
        return f"**{formatted}**"  # Markdown加粗
    return formatted


def normalize_ticker(ticker: str) -> str:
    """
    标准化股票代码（用于yfinance查询）
    
    规则:
    - 港股: 去掉多余前导0，但保留1个0 （00700.HK -> 0700.HK, 01810.HK -> 1810.HK）
    - 美股: 去掉.US后缀 （MSFT.US -> MSFT）
    
    Args:
        ticker: 原始股票代码
    
    Returns:
        标准化后的代码
    """
    ticker = ticker.upper().strip()
    
    # 港股代码：规范化前导0
    if '.HK' in ticker:
        base = ticker.replace('.HK', '')
        # 去掉前导0，但如果全是0则保留1个
        base = base.lstrip('0') or '0'
        # 如果结果少于4位，补齐到4位（港股代码标准格式）
        if len(base) < 4:
            base = base.zfill(4)
        return f"{base}.HK"
    
    # 美股代码：去掉.US后缀（yfinance不需要）
    if '.US' in ticker:
        return ticker.replace('.US', '')
    
    return ticker


def get_currency_from_ticker(ticker: str) -> str:
    """
    根据股票代码推断货币
    
    Args:
        ticker: 股票代码
    
    Returns:
        货币代码 (USD, HKD, CNY)
    """
    if '.HK' in ticker.upper():
        return 'HKD'
    elif '.SS' in ticker.upper() or '.SZ' in ticker.upper():
        return 'CNY'
    else:
        return 'USD'


def convert_currency(amount: float, from_currency: str, to_currency: str = 'USD') -> float:
    """
    货币转换（简单汇率）
    
    Args:
        amount: 金额
        from_currency: 源货币
        to_currency: 目标货币
    
    Returns:
        转换后的金额
    """
    if from_currency == to_currency:
        return amount
    
    # 简单汇率表（实际使用时应从API获取）
    rates = {
        'HKD_TO_USD': 0.128,
        'CNY_TO_USD': 0.14,
        'USD_TO_HKD': 7.8,
        'USD_TO_CNY': 7.2,
    }
    
    key = f"{from_currency}_TO_{to_currency}"
    if key in rates:
        return amount * rates[key]
    
    return amount

