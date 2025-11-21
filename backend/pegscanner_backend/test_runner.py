from django.test.runner import DiscoverRunner


class PegscannerDiscoverRunner(DiscoverRunner):
    """Ensure core apps run when no explicit test labels are provided."""

    default_apps = ['stock_research']

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        labels = list(test_labels or [])
        if not labels:
            labels = self.default_apps.copy()
        return super().build_suite(labels, extra_tests=extra_tests, **kwargs)
