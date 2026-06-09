class FilterFactory:
    _BUILTIN_LEVELS = {'TRACE': 5, 'DEBUG': 10, 'INFO': 20, 'SUCCESS': 25, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
    _CUSTOM_LEVELS = [
        {'name': 'BLOCKING', 'no': 35},
    ]
    _AUTO_NO_BASE = 31
    _LEVEL_NO = dict(_BUILTIN_LEVELS)

    @classmethod
    def _resolveEntry(cls, entry, nextNo: int) -> dict:
        if isinstance(entry, str):
            return {'name': entry, 'no': nextNo}
        if isinstance(entry, dict):
            result = {'name': entry['name'], 'no': entry.get('no', nextNo)}
            for key in ('color', 'icon'):
                if key in entry:
                    result[key] = entry[key]
            return result
        if hasattr(entry, 'name') and hasattr(entry, 'no'):
            result = {'name': entry.name, 'no': entry.no}
            for attr in ('color', 'icon'):
                val = getattr(entry, attr, None)
                if val:
                    result[attr] = val
            return result
        raise ValueError(f'Unsupported level entry: {entry}')

    @classmethod
    def make(cls, module_levels: dict, default_level: str = 'DEBUG'):
        """Build a filter function from moduleLvs config dict."""
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
