from __future__ import annotations

from flask import flash, redirect, url_for
from flask_admin import Admin, BaseView, expose

from .crawler import build_sample_payload, fetch_yfinance_payload
from .graph_store import GraphStore


class CrawlerJobAdmin(BaseView):
    def __init__(self, store: GraphStore, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._store = store

    @expose('/')
    def index(self):
        jobs = self._store.list_jobs()
        return self.render('admin/crawler_jobs.html', jobs=jobs)

    @expose('/run/<job_id>')
    def run_job(self, job_id: str):
        job = self._store.get_job(job_id)
        if not job:
            flash('Crawler job not found', 'error')
            return redirect(url_for('.index'))

        job.mark_running()
        try:
            payload = fetch_yfinance_payload(job.symbol) or build_sample_payload(job.symbol, metadata=job.metadata)
            self._store.upsert_stock_payload(payload)
            job.mark_completed()
            flash(f'Job for {job.symbol} completed', 'success')
        except Exception as exc:  # pragma: no cover - admin actions are manual
            job.mark_failed(str(exc))
            flash(f'Job failed: {exc}', 'error')
        return redirect(url_for('.index'))


def register_admin(app, store: GraphStore) -> None:
    admin = Admin(app, name='PEG Scanner Admin')
    admin.add_view(CrawlerJobAdmin(store, name='Crawler Jobs', endpoint='crawler_jobs'))
