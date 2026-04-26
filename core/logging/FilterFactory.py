class FilterFactory:
    _LEVEL_NO = {'TRACE': 5, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}

    @classmethod
    def make(cls, module_levels: dict, default_level: str = 'DEBUG'):
        """Build a filter function from module_levels config dict."""
        # Sort by length desc so more-specific prefix wins
        sorted_rules = sorted(module_levels.items(), key=lambda x: len(x[0]), reverse=True)
        default_no = cls._LEVEL_NO.get(default_level.upper(), 10)
        def _filter(record):
            name = record['name']
            for prefix, level in sorted_rules:
                if name == prefix or name.startswith(prefix + '.'):
                    return record['level'].no >= cls._LEVEL_NO.get(level.upper(), default_no)
            return record['level'].no >= default_no
        return _filter

    pass
