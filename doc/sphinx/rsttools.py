from os import linesep
import inspect
import types

_replacements = dict()
_replacements['mod'] = {}
_replacements['const'] = {}
_replacements['func'] = {}
_replacements['attr'] = {}
_replacements['meth'] = dict.fromkeys(('range()',))
_replacements['exc'] = {}
_replacements['obj'] = {}
_replacements['class'] = dict.fromkeys(('int', 'float', 'str', 'tuple', 'list', 'dict'))

_replacements['mod']['datetime'] = 'datetime <datetime>'
_replacements['class']['datetime.datetime'] = 'datetime.datetime <datetime.datetime>'
_replacements['class']['datetime.timedelta'] = 'datetime.timedelta <datetime.timedelta>'
_replacements['class']['datetime.date'] = 'datetime.date <datetime.date>'
_replacements['meth']['datetime.date.today()'] = 'datetime.date.today() <datetime.date.today>'

def _replacements_from_pkg(_replacements, pkg, spr=None):
    if spr is None:
        _replacements['mod'][pkg.__name__] = None
        n = pkg.__name__ + '.'
    else:
        n = spr.__name__ + '.'
    for k, v in inspect.getmembers(pkg):
    #for k, v in [(name, getattr(pkg, name)) for name in sorted(dir(pkg))]:
        if not k.startswith('_') and inspect.getmodule(v) and inspect.getmodule(v).__name__.startswith(pkg.__name__):
            if inspect.ismodule(v):
                # mod -> 'datetime, datetime <datetime
                _replacements['mod'][n + k] = '%s <%s>' % (n + k, n + k)
                _replacements = _replacements_from_pkg(_replacements, v, pkg)
            elif inspect.isclass(v) and issubclass(v, Exception):
                # exc  -> 'ValueError', 'ValueError <ValueError>'
                _replacements['exc'][k] = '%s <%s>' % (k, n + k)
            elif inspect.isclass(v):
                # cls  -> 'date', 'date <datetime.date>'        # isclass(x)
                _replacements['class'][k] = '%s <%s>' % (k, n + k)
                # init -> 'date()', 'date() <datetime.date>'    # isclass(x)
                _replacements['class'][k + '()'] = '%s() <%s>' % (k, n + k)
                if spr is None:
                    _replacements = _replacements_from_cls(_replacements, v, pkg)
                else:
                    _replacements = _replacements_from_cls(_replacements, v, spr)
            elif inspect.isfunction(v):
                # func -> 'foo()', 'pkg.foo() <foo()>'
                _replacements['func'][k + '()'] = '%s() <%s>' % (k, n + k)
            else:
                # attr -> 'DO', 'date.year <datetime.date.year>'
                _replacements['attr'][k] = '%s <%s>' % (k, n + k)
    return _replacements


def _replacements_from_cls(_replacements, cls, pkg=None):
    n = cls.__name__ + '.'
    p = (pkg.__name__ + '.') if pkg else ''
    for k, v in inspect.getmembers(cls):
        if not k.startswith('_'):
            if isinstance(v, types.MethodType) or isinstance(v, types.FunctionType) or inspect.ismethoddescriptor(v):
                # meth -> 'today()', 'date.today() <datetime.date.today>'
                _replacements['meth'][n + k + '()'] = '%s() <%s>' % (n + k, p + n + k)
            elif inspect.isfunction(v):
                # meth -> 'today()', 'date.today() <datetime.date.today>'
                _replacements['meth'][n + k + '()'] = '%s() <%s>' % (n + k, p + n + k)
            else:
                # attr -> 'year', 'date.year <datetime.date.year>'
                _replacements['attr'][n + k] = '%s <%s>' % (n + k, p + n[:-1])
    return _replacements


def _replacements_str(_replacements):
    _lines = []
    for c, d in _replacements.items():
        for k, v in d.items():
            s = k if v is None else v
            _lines.append(".. |%s| replace:: :%s:`%s`" % (k, c, s))
    return """   x""".replace('x', (linesep + '   ').join(_lines))


if __name__ == '__main__':
    import datetime
    import businessdate as pkg
    # _replacements = _replacements_from_pkg(_replacements, datetime)
    _replacements = _replacements_from_pkg(_replacements, pkg)
    #_replacements = _replacements_from_cls(_replacements, datetime.date, datetime)
    print(_replacements_str(_replacements))