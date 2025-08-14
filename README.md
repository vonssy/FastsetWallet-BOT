# FastSet Wallet BOT
FastSet Wallet BOT

- Register Here: [FastSet Wallet](https://wallet.fastset.xyz/)
- Click Setting or Wallet Icon
- Copy & Save Your Private Key

## Features

  - Auto Get Account Information
  - Auto Run With Proxy - `Choose 1`
  - Auto Run Without Proxy - `Choose 2`
  - Auto Rotate Invalid Proxies - `y` or `n`
  - Auto Request Drips For All Tokens
  - Auto Make Transfer to Random Address
  - Multi Accounts

## Requiremnets

- Make sure you have Python3.9 or higher installed and pip.

## Instalation

1. **Clone The Repositories:**
   ```bash
   git clone https://github.com/vonssy/FastsetWallet-BOT.git
   ```
   ```bash
   cd FastsetWallet-BOT
   ```

2. **Install Requirements:**
   ```bash
   pip install -r requirements.txt #or pip3 install -r requirements.txt
   ```

## Configuration

- **accounts.txt:** You will find the file `accounts.txt` inside the project directory. Make sure `accounts.txt` contains data that matches the format expected by the script. Here are examples of file formats:
  ```bash
    your_private_key_1 (without 0x)
    your_private_key_2 (without 0x)
  ```

- **proxy.txt:** You will find the file `proxy.txt` inside the project directory. Make sure `proxy.txt` contains data that matches the format expected by the script. Here are examples of file formats:
  ```bash
    ip:port # Default Protcol HTTP.
    protocol://ip:port
    protocol://user:pass@ip:port
  ```

- **.env:** You will find the file `.env` inside the project directory. Make sure `.env` contains data that matches the format expected by the script. Here are examples of file formats:
  ```bash
    SET_AMOUNT = 1
    USDC_AMOUNT = 1
    ETH_AMOUNT = 0.0001
    SOL_AMOUNT = 0.1
    BTC_AMOUNT = 0.0001

    MIN_DELAY = 5
    MAX_DELAY = 10
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