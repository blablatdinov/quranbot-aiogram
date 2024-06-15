<!---
The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
-->
# Поиск мутантов в коде

Инструмент mutmut удаляет декораторы для создания мутантов. Однако декораторы `elegant`, `final`, `override` проверяются
в `mypy`, поэтому при поиске мутантов их можно удалить:

```bash
sd '@elegant\n' '' **/*.py
sd '@final\n' '' **/*.py
sd '    @override\n' '' **/*.py
sd ', override' '' **/*.py
sd 'from typing import override\n' '' **/*.py
sd 'TypeAlias,' '' **/*.py
```

Также мы можем не мутировать код в декораторе `@attrs.define(frozen=True)`, т. к. в проекте нет кода и тестов, мутирующих
эти объекты:

```bash
sd '@attrs.define(.+)' '@attrs.define' **/*.py
```

Поиск мутантов

```bash
poetry run mutmut run
```
