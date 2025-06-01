# DDAI Network BOT
DDAI Network BOT

- Register Here : [DDAI Network](https://app.ddai.network/register?ref=TUEPDwXT)
- Use Code `TUEPDwXT`

## Features

  - Auto Get Account Information
  - Auto Run With [Monosans](https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt) Proxy - `Choose 1`
  - Auto Run With Private Proxy - `Choose 2`
  - Auto Run Without Proxy - `Choose 3`
  - Auto Rotate Invalid Proxies - `y` or `n`
  - Auto Perform Onchain Trigger
  - Auto Complete Available Missions
  - Multi Accounts With Threads

## Requiremnets

- Make sure you have Python3.9 or higher installed and pip.

## Instalation

1. **Clone The Repositories:**
   ```bash
   git clone https://github.com/vonssy/Ddai-BOT.git
   ```
   ```bash
   cd Ddai-BOT
   ```

2. **Install Requirements:**
   ```bash
   pip install -r requirements.txt #or pip3 install -r requirements.txt
   ```

## Configuration

- **accounts.json:** You will find the file `accounts.json` inside the project directory. `accounts.json` is used for `email and password login method`, it will require `2captcha_key`. Make sure `accounts.json` contains data that matches the format expected by the script. Here are examples of file formats:
  ```json
  [
      {
          "Email": "your_email_address_1",
          "Password": "your_password_1"
      },
      {
          "Email": "your_email_address_2",
          "Password": "your_password_2"
      }
  ]
  ```

- **2captcha_key.txt:** Enter your 2captcha_key here, you can buy it on the official website [2captcha.com](https://2captcha.com/)

- **setup.py:** You can run setup.py to get `access_token` and `refresh_token`, both tokens will be stored in `tokens.json`
  ```bash
  python setup.py #or python3 setup.py
  ```

- **tokens.json:** You will find the file `tokens.json` inside the project directory. If you don't have 2captcha_key, you can manually fill in `access_token` and `refresh_token` in `tokens.json`. Make sure `tokens.json` contains data that matches the format expected by the script. Here are examples of file formats:
  ```json
  [
      {
          "Email": "your_email_address_1",
          "accessToken": "your_access_token_1",
          "refreshToken": "your_refresh_token_1"
      },
      {
          "Email": "your_email_address_2",
          "accessToken": "your_access_token_2",
          "refreshToken": "your_refresh_token_2"
      }
  ]
  ```

- **proxy.txt:** You will find the file `proxy.txt` inside the project directory. Make sure `proxy.txt` contains data that matches the format expected by the script. Here are examples of file formats:
  ```bash
    ip:port # Default Protcol HTTP.
    protocol://ip:port
    protocol://user:pass@ip:port
  ```

## Run

```bash
python bot.py #or python3 bot.py
```

## Buy Me a Coffee

- **EVM:** 0xe3c9ef9a39e9eb0582e5b147026cae524338521a
- **TON:** UQBEFv58DC4FUrGqinBB5PAQS7TzXSm5c1Fn6nkiet8kmehB
- **SOL:** E1xkaJYmAFEj28NPHKhjbf7GcvfdjKdvXju8d8AeSunf
- **SUI:** 0xa03726ecbbe00b31df6a61d7a59d02a7eedc39fe269532ceab97852a04cf3347

Thank you for visiting this repository, don't forget to contribute in the form of follows and stars.
If you have questions, find an issue, or have suggestions for improvement, feel free to contact me or open an *issue* in this GitHub repository.

**vonssy**