# Требования к разделу "Время намаза"

При отправке сообщения "Время намаза" пользователь должен получить сообщение с [временем намаза](glossary.md#Сообщение-с-временем-намаза)

Если у пользователя не установлен город, то ему должно вернуться [сообщение с предложением выбрать город](glossary.md#Сообщение-с-предложением-выбрать-город)

Пользователь может отправить свое местоположение и по координатам ему присвоится город

Пример диалога с отправкой местоположения:

```mermaid
sequenceDiagram
    actor User
    User->>Bot: Время намаза
    Bot->>User: Вы не указали город, отправьте местоположение или воспользуйтесь поиском
    User->>Bot: <location>
    Bot->>User: Вам будет приходить время намаза для г. Казань
```

Пример диалога с отправкой местоположения:

```mermaid
sequenceDiagram
    actor User
    User->>Bot: Время намаза
    Bot->>User: Вы не указали город, отправьте местоположение или воспользуйтесь поиском
    User->>Bot: Нажатие на кнопку "Поиск города"
    User->>User: Режим инлайн поиска
    User->>Bot: @Quran_365_bot Казань
    Bot->>User: Список городов для выбора
    User->>Bot: <Выбор города из списка>
    Bot->>User: Вам будет приходить время намаза для г. Казань
```