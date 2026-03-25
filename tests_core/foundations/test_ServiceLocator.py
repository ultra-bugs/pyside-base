"""
Unit tests for core.ServiceLocator – FQN/type-based lookup feature.
"""
import pytest

from core.ServiceLocator import ServiceLocator


# ---------------------------------------------------------------------------
# Dummy service classes used across tests
# ---------------------------------------------------------------------------

class DummyServiceA:
    pass


class DummyServiceB:
    cleanedUp = False

    def cleanup(self):
        DummyServiceB.cleanedUp = True


class DummyServiceC:
    pass


# ---------------------------------------------------------------------------
# Global singleton – register / get
# ---------------------------------------------------------------------------

class TestGlobalSingletons:
    def setup_method(self):
        self.sl = ServiceLocator()

    def test_register_and_get_by_string_key(self):
        svc = DummyServiceA()
        self.sl.register('my_svc', svc)
        assert self.sl.get('my_svc') is svc

    def test_get_missing_key_returns_default(self):
        assert self.sl.get('not_there') is None
        sentinel = object()
        assert self.sl.get('not_there', sentinel) is sentinel

    def test_register_instance_auto_key(self):
        svc = DummyServiceA()
        self.sl.register(svc)
        assert self.sl.get(DummyServiceA) is svc

    def test_register_by_class_explicit(self):
        svc = DummyServiceA()
        self.sl.register(DummyServiceA, svc)
        assert self.sl.get(DummyServiceA) is svc

    def test_get_by_class_returns_same_instance(self):
        svc = DummyServiceA()
        self.sl.register(DummyServiceA, svc)
        assert self.sl.get(DummyServiceA) is svc

    def test_overwrite_existing_key_no_raise(self):
        svc1 = DummyServiceA()
        svc2 = DummyServiceA()
        self.sl.register('key', svc1)
        self.sl.register('key', svc2)
        assert self.sl.get('key') is svc2

    def test_resolve_key_raises_on_invalid_type(self):
        with pytest.raises(TypeError):
            ServiceLocator._resolveKey(123)  # noqa: SLF001


# ---------------------------------------------------------------------------
# Scoped instances – registerScoped / getScopedByType / releaseScope
# ---------------------------------------------------------------------------

class TestScopedServices:
    def setup_method(self):
        self.sl = ServiceLocator()
        self.tag = 'task-uuid-1234'

    def test_register_and_get_scoped_list(self):
        svc = DummyServiceA()
        self.sl.registerScoped(self.tag, svc)
        assert svc in self.sl.getScoped(self.tag)

    def test_duplicate_skipped(self):
        svc = DummyServiceA()
        self.sl.registerScoped(self.tag, svc)
        self.sl.registerScoped(self.tag, svc)
        assert len(self.sl.getScoped(self.tag)) == 1

    def test_get_scoped_by_type(self):
        svcA = DummyServiceA()
        svcB = DummyServiceB()
        self.sl.registerScoped(self.tag, svcA)
        self.sl.registerScoped(self.tag, svcB)
        assert self.sl.getScopedByType(self.tag, DummyServiceA) is svcA
        assert self.sl.getScopedByType(self.tag, DummyServiceB) is svcB

    def test_get_scoped_by_type_returns_none_if_not_found(self):
        self.sl.registerScoped(self.tag, DummyServiceA())
        assert self.sl.getScopedByType(self.tag, DummyServiceC) is None

    def test_release_scope_calls_cleanup(self):
        DummyServiceB.cleanedUp = False
        svc = DummyServiceB()
        self.sl.registerScoped(self.tag, svc)
        self.sl.releaseScope(self.tag)
        assert DummyServiceB.cleanedUp is True

    def test_release_scope_removes_tag(self):
        self.sl.registerScoped(self.tag, DummyServiceA())
        self.sl.releaseScope(self.tag)
        assert self.sl.getScoped(self.tag) == []

    def test_release_nonexistent_tag_is_noop(self):
        self.sl.releaseScope('no-such-tag')
