<a id="readme-top"></a>

[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![MIT License][license-shield]][license-url]
[![Telegram][telegram-shield]][telegram-url]
[![Python][Python.com]][Python-url]

<br />
<div align="center">
  <a href="https://t.me/TVerse?startapp=galaxy-0001a845e80004f232c60000a43a7f">
    <img src="https://i.ibb.co/Q6Lwvdt/photo-2024-11-18-23-50-52-modified.png" alt="TinyVerse Logo" width="100" height="100">
  </a>

<h3 align="center">Auto <a href="https://t.me/TVerse?startapp=galaxy-0001a845e80004f232c60000a43a7f">@TVerse 2.0</a></h3>
  <p align="center">
    Auto <a href="https://t.me/TVerse?startapp=galaxy-0001a845e80004f232c60000a43a7f">@TVerse</a> Farming Script
    <br />
    <a href="https://github.com/m3taphor/TinyVerse/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    •
    <a href="https://github.com/m3taphor/TinyVerse/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-feature">Key Feature</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#obtain-telegram-api">Obtain Telegram API</a></li>
        <li><a href="#env-management">Env Management</a></li>
        <li><a href="#stars-env-settings">Stars Env Settings</a></li>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#quick-start">Quick Start</a></li>
        <li><a href="#manual-installation">Manual Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#account-management">Account Management</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

## About The Project

[![TVerse][product-screenshot]](https://t.me/TVerse?startapp=galaxy-0001a845e80004f232c60000a43a7f)

An automated script/code made by @m3taphor on [Python 3.10](https://www.python.org/downloads/release/python-3100/) for [@tverse](https://t.me/TVerse?startapp=galaxy-0001a845e80004f232c60000a43a7f) or [@TVerseAppBot](https://t.me/TVerse?startapp=galaxy-0001a845e80004f232c60000a43a7f), built using TinyVerse (Tiny-Verse/TVerse) app APIs. It supports multiple sessions through [Pyrogram](https://github.com/pyrogram/pyrogram), with custom proxy support via an `accounts.json` configuration file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Key Feature

- Multithreading
- Custom Binding on pyrogram session
  - Proxy Binding
  - User-Agent Binding
- Auto Login
- Auto Refer
- Auto Create Stars
- Auto Gift Stars
- Auto Dust Collect
- Auto Apply Boosts
- Night-Mode Sleep
- Track Bot Updates

<p align="right">(<a href="#readme-top">back to top</a>)</p>

# Getting Started

> [!WARNING]
> Please be aware that using this script may result in your [@tverse](https://t.me/TVerse?startapp=galaxy-0001a845e80004f232c60000a43a7f) account being banned due to violating terms of service (e.g., cheating). Use at your own risk. The author assumes no responsibility for any consequences.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Obtain Telegram API

> [!WARNING]
> Please do NOT share your `API ID` & `API HASH` to anyone.

1. Open your browser and go to the my.telegram.org
2. Use your Telegram phone number to log in to the developer portal. You will receive a code via Telegram to authenticate.
3. After logging in, go to the API development tools section and click on Create new application (if not exist).
4. You will need to fill out some basic information for your application:
   - `App title`: Name your app (e.g., "My Telegram Bot").
   - `Short name`: A shorter version of your app's name.
   - `URL`: You can leave this blank or enter a website URL (optional).
   - `Platform`: Choose what kind of app you are developing (e.g., "Other").
5. Once the application is created, you will see a page with your `API ID` and `API HASH`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Env Management

| Settings                         |                                           Description (Usage)                                           |
| -------------------------------- | :-----------------------------------------------------------------------------------------------------: |
| **API_ID / API_HASH**            | API Keys of telegram. Use to manage accounts, tutorial: ([#obtain-telegram-api](#obtain-telegram-api))  |
| **SUPPORT_AUTHOR**               |              Add random choice between `REF_KEY` & AUTHOR `REF_KEY` (by default - `True`)               |
| **REF_KEY**                      |      Start with refer, ID which is after `startapp=` (eg. `galaxy-0001a845e80004f232c60000a43a7f`)      |
| **TRACK_BOT_UPDATES**            |                             Track Changes in Bot API (by default - `True`)                              |
| **MAX_REQUEST_RETRY**            |                          Max retry the ratelimited request (by default - `3`)                           |
| **NIGHT_MODE**                   |                         Script will sleep on Night hours (by default - `False`)                         |
| **NIGHT_TIME**                   |            [Night Mode]: Hours of sleep on UTC Timezone [start, end] (by default - `[0, 7]`)            |
| **NIGHT_CHECKING**               |     [Night Mode]: Delay (in seconds) to check if night hours are over (by default - `[3600, 7200]`)     |
| **AUTO_CREATE_STAR**             | Auto creates star from dust, tutorial: ([#stars-env-settings](#stars-env-settings))(default - `False`)  |
| **USE_DUST_PERCENTAGE**          |                 [Stars]: Total percentage of dust use to create stars (default - `90`)                  |
| **MAKE_STARS_ALLOWED_USERNAME**  |                     [Stars]: Allowed Username to create stars (default - `["all"]`)                     |
| **MAKE_STARS_RESTRICT_USERNAME** |                       [Stars]: Restrict Username to create stars (default - `[]`)                       |
| **AUTO_GIFT_STAR**               | Auto gift stars to username, tutorial: ([#stars-env-settings](#stars-env-settings)) (default - `False`) |
| **GIFT_STAR_PERCENTAGE**         |                  [Gifts]: Total percentage of dust use to create gift (default - `90`)                  |
| **MAKE_GIFT_ALLOWED_USERNAME**   |                   [Gifts]: Allowed Username to create gift code (default - `["all"]`)                   |
| **MAKE_GIFT_RESTRICT_USERNAME**  |                     [Gifts]: Restrict Username to create gift code (default - `[]`)                     |
| **GIFT_TO_USERNAME**             |                         [Gifts]: Username(s) to use gift code (default - `[]`)                          |
| **AUTO_REDEEM_CODE**             |                        [Gifts]: Auto Redeem generated gift code (default - `[]`)                        |
| **AUTO_COLLECT_DUST**            |                           Auto collect Star dust of Galaxy (default - `True`)                           |
| **AUTO_APPLY_BOOST**             |                              Auto apply remaning Boost (default - `True`)                               |
| **EXTRA_BOOST_DELAY**            |       [Boost]: Delay after auto-collect Boost is Done before proceeding (default - `[100, 500]`)        |
| **SLEEP_TIME**                   |           Sleep delay (in seconds) before restarting session again (default - `[2700, 4200]`)           |
| **START_DELAY**                  |                       Delay (in seconds) to start process (default - `[5, 100]`)                        |
| **IN_USE_SESSIONS_PATH**         |        Path of text file for appending in-use session (default - `bot/config/used_sessions.txt`)        |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Stars Env Settings

**Star Creation**

- `AUTO_CREATE_STAR`: Enables automatic creation of stars from star dust. Allowed values: (`True`/`False`).
- `USE_DUST_PERCENTAGE`: Specifies the percentage of dust required to create stars. For example, if set to `100`, stars will be created when the dust reaches the maximum capacity (e.g., _10000/10000_). Allowed values: (`1` to `100`). For minimal dust requirement or no percentage limit, use `0`.
- `MAKE_STARS_ALLOWED_USERNAME`: Specifies usernames that are permitted to create stars. Allowed values: `["username"]` or `["username1", "username2"]`. To allow all usernames, use `["all"]`.
- `MAKE_STARS_RESTRICT_USERNAME`: Specifies usernames that are restricted from creating stars. Allowed values: `["username"]` or `["username1", "username2"]`. To disable restrictions, use `[]`.

**Gift Star Creation**

- `AUTO_GIFT_STAR`: Enables automatic creation of gift codes for stars using star dust. Allowed values: (`True`/`False`).
- `GIFT_STAR_PERCENTAGE`: Specifies the percentage of dust required to create gift codes for stars. For example, if set to `100`, gift codes will be created when the dust reaches the maximum capacity (e.g., _10000/10000_). Allowed values: (`1` to `100`). For minimal dust requirement or no percentage limit, use `0`.
- `MAKE_GIFT_ALLOWED_USERNAME`: Specifies usernames that are permitted to create gift codes for stars. Allowed values: `["username"]` or `["username1", "username2"]`. To allow all usernames, use `["all"]`.
- `MAKE_GIFT_RESTRICT_USERNAME`: Specifies usernames that are restricted from creating gift codes for stars. Allowed values: `["username"]` or `["username1", "username2"]`. To disable restrictions, use `[]`.

> [!NOTE]
> Gift codes that are "self-created" can be redeemed in the same account where they were generated. To manage this, use `MAKE_GIFT_RESTRICT_USERNAME` and `MAKE_GIFT_ALLOWED_USERNAME` before generating the code.

- `GIFT_TO_USERNAME`: Specifies usernames to gift stars with a gift code. Allowed values: `["username"]` or, for multiple usernames, a random selection from `["username1", "username2"]`. Usernames can be added or edited after the code is generated and before it is redeemed in the `gift-code.json` file.

**Gift Code Usage**

> [!NOTE]
> Ensure that the pyrogram `.session` file for the username is present in the `/sessions` folder.

> [!TIP]
> Alternatively, you can manually redeem codes in Telegram by adding the gift code in the URL: `https://t.me/tverse?startapp=gift-XXXXXX`, where `XXXXXX` is your code.

- `AUTO_REDEEM_CODE`: Automatically redeems gift codes using the `gift-code.json` file. Allowed values: (`True`/`False`).

**Adding Gift Code manually**

You can handle your gift code or add/change codes by editing the `gift-codes.json` file found in the main directory.
Here's an example of the `gift-codes.json` file:

```json
[
  {
    "incorrectCodes": [],
    "usedCodes": [],
    "generatedCodes": [
      {
        "code": "XXXXXXX",
        "amount": 100,
        "forUser": "username"
      }
    ]
  }
]
```

In this file, ensure the codes are correct. The amount and username can be edited as needed.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Prerequisites

> [!IMPORTANT]
> Make sure you have only [Python 3.10](https://www.python.org/downloads/release/python-3100/), or you will encounter errors.

**Check the python version before installation**

- Windows OS

  ```sh
  python -v
  ```

- Linux OS
  ```sh
  python3 —version
  ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Quick Start

1. Clone the repo
   ```sh
   git clone https://github.com/m3taphor/TinyVerse.git
   ```
2. Obtain Api Keys from my.telegram.org, tutorial: ([#obtain-telegram-api](#obtain-telegram-api))
3. Edit your .env configuration, tutorial: ([#env-management](#env-management))
4. Run Batch/Bash file according to your operating system.
   - Run (Windows OS)
   ```sh
   run.bat
   ```
   - Run (Linux OS)
   ```sh
   ./run.sh
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Manual Installation

### Windows

1. Clone the repo
   ```sh
   git clone https://github.com/m3taphor/TinyVerse.git
   ```
2. Install Environment Variables
   ```sh
   python -m venv venv
   ```
3. Activate Environment Variables
   ```sh
   venv\Scripts\activate
   ```
4. Install Required Package
   ```sh
   pip install -r requirements.txt
   ```
5. Make .env file available
   ```sh
   copy .env-example .env
   ```
6. Edit .env file, as your will
   ```sh
   notepad .env
   ```
7. Run after all successful steps are done
   ```sh
   python main.py
   ```

### Linux

1. Clone the repo
   ```sh
   git clone https://github.com/m3taphor/TinyVerse.git
   ```
2. Install Environment Variables
   ```sh
   python3 -m venv venv
   ```
3. Activate Environment Variables
   ```sh
   source venv/bin/activate
   ```
4. Install Required Package
   ```sh
   pip3 install -r requirements.txt
   ```
5. Make .env file available
   ```sh
   cp .env-example .env
   ```
6. Edit .env file, as your will
   ```sh
   nano .env
   ```
7. Run after all successful steps are done
   ```sh
   python3 main.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

> [!TIP]
> Edit `.env` file before running script; Checkout ([#env-management](#env-management))

After the script is successfully installed, you will see two options:

1. **Run Bot**
2. **Create Session**

If you don’t have a **Pyrogram** session for your Telegram account, select **Option 2** to create one. You will need to enter your registered Telegram phone number, the login OTP sent to your Telegram account, and your 2FA password. This will save your Pyrogram session in a folder named _sessions_

> [!WARNING]
> Do not share your session file with anyone, as it may lead to losing access to your Telegram account.

If you already have a existing **Pyrogram** session, simply place it in the _sessions_ folder, then choose **Option 1 (Run Bot)** to start the mining or farming process.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Account Management

You can manage your account or modify your proxy by editing the `accounts.json` file located in the sessions folder.
Here’s an example of `accounts.json`:

```json
[
  {
    "session_name": "name_example",
    "user_agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "proxy": "type://user:pass:ip:port"  # "proxy": "" - if you dont use proxy
  }
]
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License.
The GNU General Public License is a free, copyleft license for software and other kinds of works.

More Info on [LICENSE](https://github.com/m3taphor/TinyVerse/blob/main/LICENSE) file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

[forks-shield]: https://img.shields.io/github/forks/m3taphor/TinyVerse.svg?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0Ij48cGF0aCBkPSJNOC43NSAxOS4yNWEzLjI1IDMuMjUgMCAxIDEgNi41IDAgMy4yNSAzLjI1IDAgMCAxLTYuNSAwWk0xNSA0Ljc1YTMuMjUgMy4yNSAwIDEgMSA2LjUgMCAzLjI1IDMuMjUgMCAwIDEtNi41IDBabS0xMi41IDBhMy4yNSAzLjI1IDAgMSAxIDYuNSAwIDMuMjUgMy4yNSAwIDAgMS02LjUgMFpNNS43NSA2LjVhMS43NSAxLjc1IDAgMSAwLS4wMDEtMy41MDFBMS43NSAxLjc1IDAgMCAwIDUuNzUgNi41Wk0xMiAyMWExLjc1IDEuNzUgMCAxIDAtLjAwMS0zLjUwMUExLjc1IDEuNzUgMCAwIDAgMTIgMjFabTYuMjUtMTQuNWExLjc1IDEuNzUgMCAxIDAtLjAwMS0zLjUwMUExLjc1IDEuNzUgMCAwIDAgMTguMjUgNi41WiIgZmlsbD0iI2ZmZmZmZiIvPjxwYXRoIGQ9Ik02LjUgNy43NXYxQTIuMjUgMi4yNSAwIDAgMCA4Ljc1IDExaDYuNWEyLjI1IDIuMjUgMCAwIDAgMi4yNS0yLjI1di0xSDE5djFhMy43NSAzLjc1IDAgMCAxLTMuNzUgMy43NWgtNi41QTMuNzUgMy43NSAwIDAgMSA1IDguNzV2LTFaIiBmaWxsPSIjZmZmZmZmIi8+PHBhdGggZD0iTTExLjI1IDE2LjI1di01aDEuNXY1aC0xLjVaIiBmaWxsPSIjZmZmZmZmIi8+PC9zdmc+
[forks-url]: https://github.com/m3taphor/TinyVerse/network/members
[stars-shield]: https://img.shields.io/github/stars/m3taphor/TinyVerse.svg?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNiAxNiIgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2Ij4NCiAgPHBhdGggZD0iTTggLjI1YS43NS43NSAwIDAgMSAuNjczLjQxOGwxLjg4MiAzLjgxNSA0LjIxLjYxMmEuNzUuNzUgMCAwIDEgLjQxNiAxLjI3OWwtMy4wNDYgMi45Ny43MTkgNC4xOTJhLjc1MS43NTEgMCAwIDEtMS4wODguNzkxTDggMTIuMzQ3bC0zLjc2NiAxLjk4YS43NS43NSAwIDAgMS0xLjA4OC0uNzlsLjcyLTQuMTk0TC44MTggNi4zNzRhLjc1Ljc1IDAgMCAxIC40MTYtMS4yOGw0LjIxLS42MTFMNy4zMjcuNjY4QS43NS43NSAwIDAgMSA4IC4yNVptMCAyLjQ0NUw2LjYxNSA1LjVhLjc1Ljc1IDAgMCAxLS41NjQuNDFsLTMuMDk3LjQ1IDIuMjQgMi4xODRhLjc1Ljc1IDAgMCAxIC4yMTYuNjY0bC0uNTI4IDMuMDg0IDIuNzY5LTEuNDU2YS43NS43NSAwIDAgMSAuNjk4IDBsMi43NyAxLjQ1Ni0uNTMtMy4wODRhLjc1Ljc1IDAgMCAxIC4yMTYtLjY2NGwyLjI0LTIuMTgzLTMuMDk2LS40NWEuNzUuNzUgMCAwIDEtLjU2NC0uNDFMOCAyLjY5NFoiIGZpbGw9IiNmZmZmZmYiPjwvcGF0aD4NCjwvc3ZnPg0K
[stars-url]: https://github.com/m3taphor/TinyVerse/stargazers
[license-shield]: https://img.shields.io/github/license/m3taphor/TinyVerse.svg?style=for-the-badge
[license-url]: https://github.com/m3taphor/TinyVerse/blob/main/LICENSE
[telegram-shield]: https://img.shields.io/badge/Telegram-29a9eb?style=for-the-badge&logo=telegram&logoColor=white
[telegram-url]: https://telegram.me/m3taphor
[product-screenshot]: https://i.ibb.co/LrSLGV3/image.png
[Python.com]: https://img.shields.io/badge/python%203.10-3670A0?style=for-the-badge&logo=python&logoColor=ffffff
[Python-url]: https://www.python.org/downloads/release/python-3100/
