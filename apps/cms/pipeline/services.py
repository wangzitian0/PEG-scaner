"""
Pipeline Services - Workflow operations using Django FSM.

Uses:
- Django models with django-fsm for state management
- libs/schema/whitelist/ for field validation
- libs/neo4j_models/ for graph operations
"""

import uuid
from typing import Any, Dict, List

from django.contrib.auth.models import User

from libs.neo4j_models import Company, DailyQuote, DataSource, EarningsReport, NewsArticle
from libs.schema.whitelist import validate_company, validate_earnings, validate_news, validate_quote

from .models import DataBatchRecord


class PipelineService:
    """Manages data pipeline workflow using Django FSM."""
    
    VALIDATORS = {
        'company': validate_company,
        'quote': validate_quote,
        'earnings': validate_earnings,
        'news': validate_news,
    }
    
    MODELS = {
        'company': Company,
        'quote': DailyQuote,
        'earnings': EarningsReport,
        'news': NewsArticle,
    }
    
    def create_batch(
        self,
        source: str,
        data_type: str,
        raw_data: List[Dict[str, Any]],
        user: User = None,
    ) -> DataBatchRecord:
        """Create a new data batch record."""
        batch_id = f"{source}_{data_type}_{uuid.uuid4().hex[:8]}"
        
        batch = DataBatchRecord.objects.create(
            batch_id=batch_id,
            source=source,
            data_type=data_type,
            record_count=len(raw_data),
            created_by=user,
        )
        
        # Store raw data in Neo4j DataBatch node
        from libs.neo4j_models import DataBatch as Neo4jDataBatch
        neo4j_batch = Neo4jDataBatch(
            batch_id=batch_id,
            source=source,
            data_type=data_type,
            raw_data=raw_data,
            record_count=len(raw_data),
            status='raw',
        )
        neo4j_batch.save()
        batch.neo4j_uid = neo4j_batch.uid
        batch.save()
        
        return batch
    
    def clean_batch(self, batch: DataBatchRecord) -> DataBatchRecord:
        """Clean and validate batch data using FSM transition."""
        from libs.neo4j_models import DataBatch as Neo4jDataBatch
        
        # Start cleaning
        batch.start_cleaning()
        batch.save()
        
        # Get Neo4j batch
        neo4j_batch = Neo4jDataBatch.nodes.get(batch_id=batch.batch_id)
        
        # Validate using whitelist
        validator = self.VALIDATORS.get(batch.data_type)
        errors = []
        
        if validator:
            for record in neo4j_batch.raw_data or []:
                is_valid, record_errors = validator(record)
                if record_errors:
                    errors.append({'record': record, 'errors': record_errors})
        
        # Update Neo4j batch
        neo4j_batch.cleaned_data = neo4j_batch.raw_data  # All fields pass through
        neo4j_batch.validation_errors = errors
        neo4j_batch.error_count = len(errors)
        neo4j_batch.status = 'clean'
        neo4j_batch.save()
        
        # Finish cleaning
        batch.finish_cleaning(error_count=len(errors))
        batch.save()
        
        return batch
    
    def submit_for_review(self, batch: DataBatchRecord) -> DataBatchRecord:
        """Submit batch for review."""
        from libs.neo4j_models import DataBatch as Neo4jDataBatch
        
        batch.submit_for_review()
        batch.save()
        
        # Update Neo4j
        neo4j_batch = Neo4jDataBatch.nodes.get(batch_id=batch.batch_id)
        neo4j_batch.status = 'reviewing'
        neo4j_batch.save()
        
        return batch
    
    def approve_batch(self, batch: DataBatchRecord, reviewer: User, note: str = '') -> DataBatchRecord:
        """Approve batch."""
        from libs.neo4j_models import DataBatch as Neo4jDataBatch
        
        batch.approve(reviewer=reviewer, note=note)
        batch.save()
        
        # Update Neo4j
        neo4j_batch = Neo4jDataBatch.nodes.get(batch_id=batch.batch_id)
        neo4j_batch.status = 'approved'
        neo4j_batch.reviewer = reviewer.username
        neo4j_batch.save()
        
        return batch
    
    def commit_batch(self, batch: DataBatchRecord) -> int:
        """Commit approved batch to Neo4j."""
        from libs.neo4j_models import DataBatch as Neo4jDataBatch
        
        neo4j_batch = Neo4jDataBatch.nodes.get(batch_id=batch.batch_id)
        
        model_class = self.MODELS.get(batch.data_type)
        if not model_class:
            raise ValueError(f"Unknown data type: {batch.data_type}")
        
        source = self._get_or_create_source(batch.source)
        count = 0
        
        for record in neo4j_batch.cleaned_data or []:
            node = self._upsert_record(model_class, record)
            if node and hasattr(node, 'provenance'):
                try:
                    node.provenance.connect(source)
                except:
                    pass
            count += 1
        
        # Update states
        batch.commit()
        batch.save()
        
        neo4j_batch.status = 'committed'
        neo4j_batch.save()
        
        return count
    
    def _get_or_create_source(self, name: str) -> DataSource:
        try:
            return DataSource.nodes.get(name=name)
        except DataSource.DoesNotExist:
            source = DataSource(name=name, source_type="api")
            source.save()
            return source
    
    def _upsert_record(self, model_class, record: Dict[str, Any]):
        """Upsert a single record."""
        if model_class == Company:
            ticker = record.get('ticker', '').upper()
            try:
                obj = Company.nodes.get(ticker=ticker)
                for k, v in record.items():
                    if hasattr(obj, k) and k != 'ticker':
                        setattr(obj, k, v)
                obj.save()
            except Company.DoesNotExist:
                obj = Company(**record)
                obj.ticker = ticker
                obj.save()
            return obj
        
        elif model_class == DailyQuote:
            ticker = record.get('ticker', '').upper()
            date = record.get('date')
            existing = DailyQuote.nodes.filter(ticker=ticker, date=date).first()
            if existing:
                for k, v in record.items():
                    if hasattr(existing, k):
                        setattr(existing, k, v)
                existing.save()
                return existing
            obj = DailyQuote(**record)
            obj.ticker = ticker
            obj.save()
            return obj
        
        return None


# Singleton
pipeline_service = PipelineService()
