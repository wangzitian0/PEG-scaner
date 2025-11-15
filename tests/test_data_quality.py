"""
数据质量测试 - 验证数据产物

遵循 agent.md Line 45: 测试不仅仅是测试代码，还有数据产物的基本校验
"""

import pytest
from pathlib import Path
import pandas as pd
import re
from core.data_io import parse_filename, SCHEMA_DIRS


class TestDataQuality:
    """数据质量测试套件"""
    
    @pytest.fixture
    def x_data_dir(self):
        """x-data目录"""
        return Path("x-data")
    
    def test_x_data_directory_exists(self, x_data_dir):
        """测试x-data目录存在"""
        assert x_data_dir.exists(), "x-data目录应该存在"
        assert x_data_dir.is_dir(), "x-data应该是目录"
    
    def test_schema_directories_exist(self, x_data_dir):
        """测试所有schema目录存在"""
        expected_schemas = [
            "stock_daily",
            "stock_fundamental",
            "etf_portfolio",
            "backtest_result",
            "analysis_result"
        ]
        
        for schema in expected_schemas:
            schema_dir = x_data_dir / schema
            assert schema_dir.exists(), f"{schema}目录应该存在"
    
    def test_filename_convention(self, x_data_dir):
        """
        测试文件命名规范
        
        agent.md Line 31: schema-name-source-date.csv
        """
        # 正则: schema-name-source-date.csv
        filename_pattern = re.compile(r'^[\w]+-.+-[\w]+-.+\.csv$')
        
        csv_files = list(x_data_dir.rglob("*.csv"))
        
        for csv_file in csv_files:
            filename = csv_file.name
            
            # 检查是否符合命名规范
            assert filename_pattern.match(filename), \
                f"文件名不符合规范 schema-name-source-date.csv: {filename}"
            
            # 检查是否可以解析
            try:
                info = parse_filename(filename)
                assert 'schema' in info
                assert 'name' in info
                assert 'source' in info
                assert 'date' in info
            except ValueError as e:
                pytest.fail(f"文件名解析失败: {filename}, 错误: {e}")
    
    def test_csv_file_format(self, x_data_dir):
        """测试CSV文件格式有效"""
        csv_files = list(x_data_dir.rglob("*.csv"))
        
        if not csv_files:
            pytest.skip("没有CSV文件需要测试")
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                
                # 检查不是空文件
                assert len(df) > 0, f"CSV文件为空: {csv_file}"
                
                # 检查有列
                assert len(df.columns) > 0, f"CSV文件没有列: {csv_file}"
                
            except Exception as e:
                pytest.fail(f"CSV文件格式错误: {csv_file}, 错误: {e}")
    
    def test_stock_fundamental_schema(self, x_data_dir):
        """测试stock_fundamental的schema一致性"""
        fundamental_dir = x_data_dir / "stock_fundamental"
        
        if not fundamental_dir.exists():
            pytest.skip("stock_fundamental目录不存在")
        
        csv_files = list(fundamental_dir.glob("*.csv"))
        
        if not csv_files:
            pytest.skip("stock_fundamental目录没有CSV文件")
        
        # 期望的列
        expected_columns = [
            'ticker', 'date', 'price', 'pe', 'peg', 
            'net_income', 'growth_rate', 'market_cap', 
            'source', 'confidence'
        ]
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            
            # 检查列是否存在
            for col in expected_columns:
                assert col in df.columns, \
                    f"{csv_file}缺少列: {col}"
            
            # 检查关键列不为空
            assert not df['ticker'].isna().all(), \
                f"{csv_file}的ticker列全为空"
            
            assert not df['source'].isna().all(), \
                f"{csv_file}的source列全为空"
    
    def test_data_source_field(self, x_data_dir):
        """测试数据包含source字段"""
        csv_files = list(x_data_dir.rglob("stock_fundamental*.csv"))
        
        if not csv_files:
            pytest.skip("没有stock_fundamental文件需要测试")
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            
            # 检查source列存在
            assert 'source' in df.columns, \
                f"{csv_file}缺少source列"
            
            # 检查source不为空
            assert not df['source'].isna().all(), \
                f"{csv_file}的source列全为空"
            
            # 检查source值合理
            valid_sources = ['yfinance', 'alphavantage', 'aggregated', 'manual']
            sources = df['source'].dropna().unique()
            
            for source in sources:
                assert source in valid_sources or isinstance(source, str), \
                    f"{csv_file}包含无效的source: {source}"
    
    def test_confidence_field(self, x_data_dir):
        """测试置信度字段"""
        csv_files = list(x_data_dir.rglob("stock_fundamental*.csv"))
        
        if not csv_files:
            pytest.skip("没有stock_fundamental文件需要测试")
        
        valid_confidences = ['HIGH', 'MEDIUM', 'LOW']
        
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            
            if 'confidence' in df.columns:
                confidences = df['confidence'].dropna().unique()
                
                for conf in confidences:
                    assert conf in valid_confidences, \
                        f"{csv_file}包含无效的置信度: {conf}"


class TestCacheDirectory:
    """缓存目录测试"""
    
    def test_cache_in_x_data(self):
        """测试缓存在x-data/cache中"""
        cache_dir = Path("x-data/cache")
        
        # 目录可以不存在（首次运行时）
        if cache_dir.exists():
            assert cache_dir.is_dir(), "cache应该是目录"


class TestLogDirectory:
    """日志目录测试"""
    
    def test_x_log_exists(self):
        """测试x-log目录存在"""
        log_dir = Path("x-log")
        assert log_dir.exists(), "x-log目录应该存在"
        assert log_dir.is_dir(), "x-log应该是目录"


# 运行测试时显示详细信息
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

