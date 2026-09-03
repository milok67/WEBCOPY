# WEBCOPY

Установка - pip install requests beautifulsoup4
Запуск - python webcopy.py

# WEBCOPY — Офлайн-копировщик веб-страниц
**WEBCOPY** — это Python-инструмент для создания локальной офлайн-копии веб-страницы вместе с её основными ресурсами.
Программа загружает HTML-страницу, находит подключённые CSS, JavaScript, изображения, шрифты и медиафайлы, сохраняет их локально и автоматически переписывает ссылки так, чтобы страница могла открываться из локальной папки.

## ✨ Возможности
* 🌐 Загрузка HTML-страницы
* 🎨 Скачивание CSS-файлов
* ⚙️ Скачивание JavaScript
* 🖼️ Скачивание изображений
* 🔤 Скачивание шрифтов
* 🎵 Скачивание аудио и видео
* 📱 Поддержка `srcset`
* 🎨 Обработка `url()` внутри CSS
* 📦 Обработка CSS `@import`
* 🔗 Автоматическая замена удалённых ссылок на локальные
* 🛡️ Защита от повторной загрузки одинаковых ресурсов
* 💾 Автоматическое создание структуры папок
* 📊 Статистика загруженных файлов и их размера
* ⚠️ Отображение ошибок загрузки
* 🌍 Автоматическое открытие готовой копии в браузере

## 📁 Структура проекта
После запуска создаётся папка примерно такого вида:

```text
copy_example-com/
├── index.html
└── assets/
    ├── css/
    ├── js/
    ├── img/
    ├── fonts/
    ├── media/
    └── other/
```

## 📦 Установка
Установите необходимые зависимости:

```bash
pip install requests beautifulsoup4
```

## 🚀 Использование
Запустите программу:

```bash
python webcopy.py
```

После запуска вставьте URL нужной страницы:

```text
Вставь ссылку на страницу → https://example.com
```

После завершения работы программа создаст локальную копию и автоматически откроет `index.html` в браузере.

## ⚙️ Ограничения
WEBCOPY работает с ресурсами, которые доступны для обычного HTTP-запроса.

Динамические функции сайта, серверная логика, базы данных, авторизация, API и JavaScript-функции, требующие удалённого сервера, не превращаются автоматически в полноценную офлайн-версию.

Файлы размером более **80 МБ** по умолчанию пропускаются.

## 🛠️ Требования
* Python 3.x
* `requests`
* `beautifulsoup4`

## 📄 Назначение
Проект предназначен для обучения веб-разработке, локального анализа структуры веб-страниц, создания тестовых копий собственных сайтов и изучения работы HTML/CSS/JS-ресурсов.
Используйте инструмент только для страниц и ресурсов, которые вы имеете право копировать и анализировать.


# WEBCOPY — Offline Web Page Copier
**WEBCOPY** is a Python tool for creating local offline copies of web pages together with their main static resources.
The tool downloads the HTML page, discovers linked CSS, JavaScript, images, fonts, and media files, saves them locally, and automatically rewrites resource paths so the copied page can be opened from a local directory.

## ✨ Features
* 🌐 HTML page downloading
* 🎨 CSS asset downloading
* ⚙️ JavaScript asset downloading
* 🖼️ Image downloading
* 🔤 Font downloading
* 🎵 Audio and video downloading
* 📱 `srcset` support
* 🎨 CSS `url()` processing
* 📦 CSS `@import` processing
* 🔗 Automatic conversion of remote links to local paths
* 🛡️ Duplicate resource protection
* 💾 Automatic directory structure creation
* 📊 Download statistics and total size reporting
* ⚠️ Download error reporting
* 🌍 Automatic opening of the generated copy in a browser

## 📁 Project Structure
After running the tool, a directory similar to this will be created:

```text
copy_example-com/
├── index.html
└── assets/
    ├── css/
    ├── js/
    ├── img/
    ├── fonts/
    ├── media/
    └── other/
```

## 📦 Installation
Install the required dependencies:

```bash
pip install requests beautifulsoup4
```

## 🚀 Usage
Run the program:

```bash
python webcopy.py
```

Enter the URL of the page you want to copy:

```text
Enter page URL → https://example.com
```

When the process is complete, WEBCOPY creates a local copy and automatically opens `index.html` in your browser.

## ⚙️ Limitations
WEBCOPY works with resources that are accessible through standard HTTP requests.

Dynamic website functionality, server-side logic, databases, authentication, APIs, and JavaScript features that depend on a remote server are not automatically converted into a fully functional offline application.

Files larger than **80 MB** are skipped by default.

## 🛠️ Requirements
* Python 3.x
* `requests`
* `beautifulsoup4`

## 📄 Purpose
The project is intended for learning web development, analyzing the structure of web pages locally, creating test copies of websites you own, and studying how HTML, CSS, and JavaScript resources work.
Use this tool only with pages and resources that you are authorized to copy and analyze.


