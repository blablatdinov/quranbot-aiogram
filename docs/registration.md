# Процесс регистрации

Пользователь отправляет сообщение `/start`, далее обработка идет по 3 сценариям:

1) Это новый пользователь [подробности](#Регистрация-нового-пользователя)
2) Этот пользователь уже зарегистрирован и активен
3) Пользователь уже есть в базе, но он был отписан на момент отправки команды `/start`

Если пользователь регистрируется, деактивируется или реактивируется, то нужно логгировать это действие в БД для статистики.

При регистрации пользователя нужно сохранить его идентификатор чата.

## Регистрация нового пользователя

При регистрации нового пользователя ему отправляется [приветственное сообщение](glossary.md#Приветственное-сообщение) и контент первого дня.

## Регистрация активного пользователя

Если пользователь уже зарегистрирован и активен, бот должен отправлять сообщение `Вы уже зарегистрированы`

## Регистрация пользователя, который отписан от бота

Если пользователь был зарегистрирован и отписался от бота, ему отправляется сообщение `Рады видеть вас снова, вы продолжите с дня 43`