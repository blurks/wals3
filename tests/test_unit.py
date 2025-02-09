from collections import defaultdict
from tempfile import mktemp
from pathlib import Path

from pyramid.httpexceptions import HTTPFound

from clld.db.models.common import ValueSet, Language
from wals3.interfaces import IBlog


def test_comment(env, request_factory, mocker):
    from wals3.views import comment

    env['registry'].registerUtility(mocker.Mock(post_url=lambda *a, **kw: '/'), IBlog)
    with request_factory(matchdict=dict(fid='51A', lid='esm')) as req:
        assert isinstance(comment(req), HTTPFound)


def test_Blog(env, mocker):
    from wals3.blog import Blog

    vs = ValueSet.first()

    class wp(object):
        def __init__(self, cats=False):
            if cats:
                self.cats = [
                    dict(id=1, name='Languages'),
                    dict(id=2, name='Chapters'),
                    dict(id=3, name=vs.parameter.chapter.area.name),
                ]
            else:
                self.cats = []

        def Client(self, *args, **kw):
            return mocker.Mock(
                get_categories=lambda: self.cats,
                set_categories=lambda c: dict(n=1),
                get_post_id_from_path=lambda p: None)

    mocker.patch('wals3.blog.wordpress', wp())
    blog = Blog(defaultdict(lambda: ''))
    blog.post_url(vs, env['request'], create=True)

    mocker.patch('wals3.blog.wordpress', wp(cats=True))
    blog = Blog(defaultdict(lambda: ''))
    blog.post_url(vs, env['request'], create=True)


def test_Matrix(env):
    from wals3.adapters import Matrix

    p = Path(mktemp())
    assert not p.exists()

    class TestMatrix(Matrix):
        def abspath(self, req):
            return p

        def query(self, req):
            return Matrix.query(self, req).filter(Language.pk < 100)

    m = TestMatrix(Language, 'wals3', description="Feature values CSV")
    m.create(env['request'], verbose=False)
    assert p.exists()
    p.unlink()

