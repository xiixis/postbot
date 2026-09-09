# -*- coding: utf-8 -*-
"""Настройки: шесть разделов, которых в боте не было.

Из чата нельзя было выдать код доступа, поменять роль, поправить показатель,
настроить повтор, отправить карусель в TikTok и прибраться. Всё это жило
только в мини-приложении, а оно требует поднятого туннеля.

Сторожится здесь то, что в кнопках ломается тихо.

Права: канал, доступ и повторы настраивает только владелец. Показать их
помощнику и ответить отказом на нажатие — хуже, чем не показывать: он будет
считать, что бот сломан, а не что ему туда нельзя.

Длина кода: предел callback_data — 64 байта, кириллица занимает по два. Имя
показателя бывает в шестьдесят символов, и адресовать его названием значит
получить молчащую кнопку ровно на длинных именах.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import навигация                                             # noqa: E402
import экраны                                                # noqa: E402


class _Настройки:
    """Дублёры всего, что читают экраны настроек."""

    def __init__(self, **как):
        self.как = {"люди": {}, "коды": 0, "открыто": 0, "показатели": [],
                    "правила": [], "подключён": False, "карусели": [],
                    "ключ": "есть"}
        self.как.update(как)
        self.было = {}

    def __enter__(self):
        import access
        import channels
        import core
        import db
        import facts
        import repeats
        import tiktok
        к = self.как
        self.было = {
            (access, "свои"): access.свои, (access, "открыто"): access.открыто,
            (access, "живых_кодов"): access.живых_кодов,
            (facts, "все"): facts.все, (facts, "подготовить"): facts.подготовить,
            (repeats, "правила"): repeats.правила,
            (tiktok, "подключён"): tiktok.подключён,
            (tiktok, "профиль"): tiktok.профиль,
            (tiktok, "ссылка_входа"): tiktok.ссылка_входа,
            (tiktok, "КЛЮЧ"): tiktok.КЛЮЧ,
            (db, "черновики"): db.черновики, (db, "расписание"): db.расписание,
            (channels, "текущий"): channels.текущий,
            (channels, "основной_выбран"): channels.основной_выбран,
            (core, "звук_выключен"): core.звук_выключен,
        }
        access.свои = lambda: к["люди"]
        access.открыто = lambda: к["открыто"]
        access.живых_кодов = lambda: к["коды"]
        facts.все = lambda: к["показатели"]
        facts.подготовить = lambda: None
        repeats.правила = lambda: к["правила"]
        tiktok.подключён = lambda: к["подключён"]
        tiktok.профиль = lambda: {"имя": "4xTube", "ник": "@4xtube"}
        tiktok.ссылка_входа = lambda *_, **__: "https://tiktok.com/auth"
        tiktok.КЛЮЧ = к["ключ"]
        db.черновики = lambda *_, **__: к["карусели"]
        db.расписание = lambda *_, **__: []
        channels.текущий = lambda: "@4xtube"
        channels.основной_выбран = lambda: True
        core.звук_выключен = lambda: False
        return self

    def __exit__(self, *_):
        for (модуль, имя), было in self.было.items():
            setattr(модуль, имя, было)


def _собрать(код: str, арг: str = "", владелец: bool = True) -> экраны.Экран:
    запись, _ = экраны.найти(код)
    return запись.собрать(экраны.Пар(чат=1, арг=арг, владелец=владелец))


def _кнопки(э: экраны.Экран) -> list:
    return [к for ряд in э.ряды for к in ряд if not isinstance(к, dict)]


def _коды(э: экраны.Экран) -> list[str]:
    return [к[1] for к in _кнопки(э)]


def _карусель(ид: int, заголовок: str) -> dict:
    return {"id": ид, "title": заголовок, "status": "draft",
            "images": '["https://a/1.jpg","https://a/2.jpg"]', "card": None}


class Разделы(unittest.TestCase):

    def test_у_владельца_все_шесть(self):
        with _Настройки():
            коды = _коды(_собрать("set"))
        for код in ("set:ch", "sound", "set:acc", "set:facts", "set:rep",
                    "set:tt", "set:clean"):
            with self.subTest(код=код):
                self.assertIn(код, коды)

    def test_помощнику_чужого_не_показываем(self):
        """Показать и ответить отказом — хуже, чем не показать вовсе."""
        with _Настройки():
            коды = _коды(_собрать("set", владелец=False))
        for скрыт in ("set:ch", "set:acc", "set:rep"):
            with self.subTest(код=скрыт):
                self.assertNotIn(скрыт, коды)
        self.assertIn("sound", коды)

    def test_числа_на_кнопках_живые(self):
        with _Настройки(показатели=[{"name": "каналов", "value": "6"}],
                        правила=[{"день": 3, "время": "19:00"}]):
            подписи = dict((к[1], к[0]) for к in _кнопки(_собрать("set")))
        self.assertIn("1", подписи["set:facts"])
        self.assertIn("1", подписи["set:rep"])

    def test_все_разделы_ведут_назад_в_настройки(self):
        for код in ("set:acc", "set:facts", "set:rep", "set:tt", "set:clean"):
            with self.subTest(код=код):
                self.assertEqual(экраны.родитель(код), "set")

    def test_чужого_внутрь_не_пускают(self):
        for код in ("set:ch", "set:acc", "set:rep"):
            with self.subTest(код=код):
                запись, _ = экраны.найти(код)
                self.assertTrue(запись.только_владельцу, код)


class Доступ(unittest.TestCase):

    def test_люди_кнопками_и_дверь_со_сроком(self):
        with _Настройки(люди={7: {"имя": "Петя", "роль": "полный"}},
                        открыто=71.6):
            э = _собрать("set:acc")
        коды = _коды(э)
        self.assertIn("set:acc:7", коды)
        self.assertIn("acnew", коды)
        подписи = dict((к[1], к[0]) for к in _кнопки(э))
        self.assertIn("72", подписи.get("shut", ""), подписи)

    def test_закрытая_дверь_предлагает_открыться(self):
        with _Настройки(открыто=0):
            self.assertIn("acopen", _коды(_собрать("set:acc")))

    def test_человек_меняет_роль_и_убирается(self):
        with _Настройки(люди={7: {"имя": "Петя", "роль": "полный"}}):
            коды = _коды(_собрать("set:acc:7", арг="7"))
        self.assertIn("acrole:7", коды)
        self.assertIn("acdel:7", коды)
        self.assertEqual(экраны.родитель("set:acc:7"), "set:acc")

    def test_ушедшего_человека_не_показываем(self):
        with _Настройки(люди={}):
            with self.assertRaises(экраны.НетЭкрана):
                _собрать("set:acc:7", арг="7")


class Показатели(unittest.TestCase):

    def test_адресуются_номером_а_не_именем(self):
        """Имя бывает в шестьдесят букв: кириллицей это сто двадцать байт."""
        длинное = "среднее число просмотров ролика за последние тридцать дней"
        with _Настройки(показатели=[{"name": длинное, "value": "1200"}]):
            коды = _коды(_собрать("set:facts"))
        for к in коды:
            with self.subTest(код=к):
                self.assertLessEqual(len(к.encode("utf-8")), 64)
        self.assertIn("fdel:0", коды)

    def test_добавление_спрашивает_словами(self):
        with _Настройки(показатели=[]):
            э = _собрать("set:facts")
        self.assertIn("fnew", _коды(э))
        self.assertTrue(э.текст.strip())


class Повторы(unittest.TestCase):

    def test_правило_переключается_тычком(self):
        with _Настройки(правила=[{"день": 3, "время": "19:00", "вид": "анонс",
                                  "включено": True}]):
            э = _собрать("set:rep")
        self.assertIn("repsw:0", _коды(э))
        self.assertIn("четверг", э.текст + "".join(к[0] for к in _кнопки(э)))

    def test_удаление_отдельным_экраном(self):
        with _Настройки(правила=[{"день": 3, "время": "19:00"}]):
            self.assertIn("set:rep:rm", _коды(_собрать("set:rep")))
            self.assertIn("reprm:0", _коды(_собрать("set:rep:rm")))
        self.assertEqual(экраны.родитель("set:rep:rm"), "set:rep")

    def test_пустые_повторы_без_кнопки_удаления(self):
        with _Настройки(правила=[]):
            коды = _коды(_собрать("set:rep"))
        self.assertNotIn("set:rep:rm", коды)
        self.assertIn("repnew", коды)


class Тикток(unittest.TestCase):

    def test_без_подключения_зовут_войти(self):
        with _Настройки(подключён=False):
            э = _собрать("set:tt")
        ссылки = [к for ряд in э.ряды for к in ряд
                  if isinstance(к, dict) and "url" in к]
        self.assertEqual(len(ссылки), 1)

    def test_подключённому_показывают_карусели(self):
        with _Настройки(подключён=True,
                        карусели=[_карусель(4, "Пять ошибок")]):
            э = _собрать("set:tt")
        self.assertIn("ttsend:4", _коды(э))
        self.assertIn("@4xtube", э.текст)

    def test_без_ключей_ни_ссылки_ни_обещаний(self):
        """Приложение TikTok не заведено: кнопка входа вела бы в никуда."""
        with _Настройки(ключ="", подключён=False):
            э = _собрать("set:tt")
        self.assertFalse([к for ряд in э.ряды for к in ряд
                          if isinstance(к, dict)])
        self.assertTrue(э.текст.strip())


class Уборка(unittest.TestCase):

    def test_спрашивает_прежде_чем_чистить(self):
        """Прибраться — это удалить файлы. Кнопка «сразу» тут неуместна."""
        with _Настройки():
            э = _собрать("set:clean")
        self.assertEqual(_коды(э), ["clean"])
        self.assertTrue(э.текст.strip())


class ОтветыСловами(unittest.TestCase):

    def setUp(self):
        import telegram as tg
        # Экран чистим тоже: вопрос словами записывает в ЭКРАН своё
        # сообщение, и оставленная запись увела бы следующий тест в сеть —
        # перерисовывать он будет уже настоящим телеграмом.
        self.было = (dict(навигация.ЖДЁМ), dict(навигация.ЭКРАН))
        навигация.ЖДЁМ.clear()
        навигация.ЭКРАН.clear()
        # Непонятный ответ бот переспрашивает — а это сообщение в чат.
        self.написать = tg.написать
        self.tg = tg
        tg.написать = lambda *а, **к: {"message_id": 1}

    def tearDown(self):
        навигация.ЖДЁМ.clear()
        навигация.ЭКРАН.clear()
        навигация.ЖДЁМ.update(self.было[0])
        навигация.ЭКРАН.update(self.было[1])
        self.tg.написать = self.написать

    def test_показатель_разбирается_на_имя_и_значение(self):
        import bot
        import facts
        записали = []
        настоящая = facts.запомнить
        facts.запомнить = lambda имя, значение: записали.append((имя, значение))
        навигация.ЖДЁМ[1] = ("показатель", {})
        try:
            bot.ответить_словами(1, "каналов: 6")
        finally:
            facts.запомнить = настоящая
        self.assertEqual(записали, [("каналов", "6")])

    def test_повтор_разбирается_на_день_и_время(self):
        import bot
        import repeats
        сохранили = []
        настоящие = (repeats.сохранить, repeats.правила)
        repeats.сохранить = lambda новые: сохранили.append(новые)
        repeats.правила = lambda: []
        навигация.ЖДЁМ[1] = ("повтор", {})
        try:
            bot.ответить_словами(1, "четверг 19:00 анонс")
        finally:
            repeats.сохранить, repeats.правила = настоящие
        self.assertEqual(len(сохранили), 1, сохранили)
        правило = сохранили[0][0]
        self.assertEqual(правило["день"], 3)
        self.assertEqual(правило["время"], "19:00")
        self.assertEqual(правило["вид"], "анонс")

    def test_непонятный_повтор_не_сохраняется(self):
        """Молча записать «каждый понедельник в 00:00» — хуже, чем переспросить."""
        import bot
        import repeats
        сохранили = []
        настоящие = (repeats.сохранить, repeats.правила)
        repeats.сохранить = lambda новые: сохранили.append(новые)
        repeats.правила = lambda: []
        навигация.ЖДЁМ[1] = ("повтор", {})
        try:
            bot.ответить_словами(1, "когда-нибудь потом")
        finally:
            repeats.сохранить, repeats.правила = настоящие
        self.assertEqual(сохранили, [])


if __name__ == "__main__":
    unittest.main()
