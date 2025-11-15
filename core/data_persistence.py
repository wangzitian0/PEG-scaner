"""
数据持久化工具

原则：数据处理的中间过程尽可能持久化，便于调试和追溯
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStep:
    """处理步骤记录"""
    step: int
    action: str
    timestamp: str
    status: str  # success, failed, warning
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class DataPipeline:
    """数据处理pipeline追踪"""
    pipeline_id: str
    ticker: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "running"  # running, success, failed
    steps: List[ProcessingStep] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []


class DataPersistence:
    """数据持久化管理器"""
    
    def __init__(self, base_dir: str = './data'):
        """
        初始化数据持久化管理器
        
        Args:
            base_dir: 数据根目录
        """
        self.base_dir = Path(base_dir)
        
        # 创建目录结构
        self.raw_dir = self.base_dir / 'raw'
        self.processed_dir = self.base_dir / 'processed'
        self.cache_dir = self.base_dir / 'cache'
        self.results_dir = self.base_dir / 'results'
        self.logs_dir = self.base_dir / 'logs'
        
        for directory in [self.raw_dir, self.processed_dir, self.cache_dir, 
                         self.results_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"数据持久化管理器初始化：{self.base_dir}")
    
    def save_raw_data(self, ticker: str, source: str, data: Dict, 
                     metadata: Optional[Dict] = None) -> Path:
        """
        保存原始数据（API响应）
        
        Args:
            ticker: 股票代码
            source: 数据源名称
            data: 原始数据
            metadata: 元数据
        
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{ticker}_{source}_{timestamp}.json"
        filepath = self.raw_dir / filename
        
        payload = {
            'ticker': ticker,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'raw_data': data,
            'metadata': metadata or {}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"保存原始数据: {filepath}")
        return filepath
    
    def save_processed_data(self, ticker: str, data: Dict, 
                           pipeline: DataPipeline) -> Path:
        """
        保存处理后的数据
        
        Args:
            ticker: 股票代码
            data: 处理后的数据
            pipeline: 处理pipeline
        
        Returns:
            保存的文件路径
        """
        date = datetime.now().strftime('%Y-%m-%d')
        filename = f"{ticker}_processed_{date}.json"
        filepath = self.processed_dir / filename
        
        payload = {
            'ticker': ticker,
            'date': date,
            'data': data,
            'pipeline': asdict(pipeline)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        logger.info(f"保存处理后数据: {filepath}")
        return filepath
    
    def create_pipeline(self, ticker: str, pipeline_id: Optional[str] = None) -> DataPipeline:
        """
        创建数据处理pipeline
        
        Args:
            ticker: 股票代码
            pipeline_id: Pipeline ID（默认自动生成）
        
        Returns:
            DataPipeline对象
        """
        if pipeline_id is None:
            pipeline_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ticker}"
        
        pipeline = DataPipeline(
            pipeline_id=pipeline_id,
            ticker=ticker,
            start_time=datetime.now().isoformat(),
            steps=[]
        )
        
        logger.info(f"创建Pipeline: {pipeline_id}")
        return pipeline
    
    def add_step(self, pipeline: DataPipeline, action: str, status: str,
                 duration_ms: Optional[float] = None, error: Optional[str] = None,
                 metadata: Optional[Dict] = None) -> ProcessingStep:
        """
        添加处理步骤
        
        Args:
            pipeline: Pipeline对象
            action: 动作描述
            status: 状态
            duration_ms: 耗时（毫秒）
            error: 错误信息
            metadata: 附加元数据
        
        Returns:
            ProcessingStep对象
        """
        step = ProcessingStep(
            step=len(pipeline.steps) + 1,
            action=action,
            timestamp=datetime.now().isoformat(),
            status=status,
            duration_ms=duration_ms,
            error=error,
            metadata=metadata
        )
        
        pipeline.steps.append(step)
        
        log_msg = f"Pipeline {pipeline.pipeline_id} - Step {step.step}: {action} - {status}"
        if status == 'failed':
            logger.error(log_msg)
        elif status == 'warning':
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        return step
    
    def complete_pipeline(self, pipeline: DataPipeline, status: str = 'success'):
        """
        完成pipeline
        
        Args:
            pipeline: Pipeline对象
            status: 最终状态
        """
        pipeline.end_time = datetime.now().isoformat()
        pipeline.status = status
        
        logger.info(f"Pipeline {pipeline.pipeline_id} 完成 - 状态: {status}, 步骤数: {len(pipeline.steps)}")
    
    def save_pipeline_log(self, pipeline: DataPipeline) -> Path:
        """
        保存pipeline日志
        
        Args:
            pipeline: Pipeline对象
        
        Returns:
            日志文件路径
        """
        date = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f"pipeline_{date}.jsonl"
        
        # 以追加模式写入（JSONL格式）
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(pipeline), ensure_ascii=False) + '\n')
        
        logger.debug(f"Pipeline日志已保存: {log_file}")
        return log_file
    
    def get_pipeline_history(self, ticker: str, days: int = 7) -> List[DataPipeline]:
        """
        获取股票的处理历史
        
        Args:
            ticker: 股票代码
            days: 查询天数
        
        Returns:
            Pipeline列表
        """
        pipelines = []
        
        for log_file in sorted(self.logs_dir.glob('pipeline_*.jsonl'), reverse=True)[:days]:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    pipeline_dict = json.loads(line)
                    if pipeline_dict.get('ticker') == ticker:
                        # 重建ProcessingStep对象
                        steps = [ProcessingStep(**step) for step in pipeline_dict.get('steps', [])]
                        pipeline_dict['steps'] = steps
                        pipelines.append(DataPipeline(**pipeline_dict))
        
        return pipelines
    
    def cleanup_old_data(self, data_type: str = 'raw', days: int = 7) -> int:
        """
        清理旧数据
        
        Args:
            data_type: 数据类型 (raw, processed)
            days: 保留天数
        
        Returns:
            清理的文件数
        """
        import time
        
        if data_type == 'raw':
            target_dir = self.raw_dir
        elif data_type == 'processed':
            target_dir = self.processed_dir
        else:
            logger.error(f"未知的数据类型: {data_type}")
            return 0
        
        cutoff_time = time.time() - (days * 24 * 3600)
        count = 0
        
        for file in target_dir.glob('*.json'):
            if file.stat().st_mtime < cutoff_time:
                file.unlink()
                count += 1
        
        if count > 0:
            logger.info(f"清理了 {count} 个 {data_type} 文件（>{days}天）")
        
        return count


# 全局实例
_persistence_manager = None


def get_persistence_manager() -> DataPersistence:
    """
    获取全局数据持久化管理器实例
    
    Returns:
        DataPersistence实例
    """
    global _persistence_manager
    if _persistence_manager is None:
        _persistence_manager = DataPersistence()
    return _persistence_manager


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    pm = DataPersistence('./data')
    
    # 测试pipeline
    pipeline = pm.create_pipeline('TEST')
    
    pm.add_step(pipeline, 'fetch_yfinance', 'success', duration_ms=1234)
    pm.add_step(pipeline, 'fetch_alpha_vantage', 'success', duration_ms=2345)
    pm.add_step(pipeline, 'cross_validation', 'success', duration_ms=123, 
                metadata={'consistency': 0.98})
    
    pm.complete_pipeline(pipeline)
    pm.save_pipeline_log(pipeline)
    
    print(f"Pipeline完成: {pipeline.pipeline_id}")
    print(f"总步骤数: {len(pipeline.steps)}")

