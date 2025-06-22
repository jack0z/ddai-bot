# DDAI Network Bot

Enhanced automated bot for DDAI Network with parallel processing, automatic error recovery, and comprehensive point logging.

## Features

✅ **Parallel Token Setup** - Process multiple accounts simultaneously for faster setup
✅ **Automatic Re-setup** - Automatically re-authenticate accounts when refresh tokens fail (403 errors)
✅ **Point Logging** - Track and log points to MongoDB database with comprehensive statistics
✅ **Proxy Support** - Free proxyscrape, private proxies, or no proxy modes
✅ **Mission Completion** - Automatic mission claiming
✅ **Throughput Monitoring** - Real-time throughput percentage tracking
✅ **Error Recovery** - Robust error handling and automatic recovery

## Requirements

- Python 3.8+
- 2captcha API key (for solving captcha during setup)
- MongoDB database (optional, for point logging)

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create your configuration files:

### accounts.json
Create `accounts.json` with your account credentials:
```json
[
    {
        "Email": "your-email@example.com",
        "Password": "your-password"
    },
    {
        "Email": "another-email@example.com",
        "Password": "another-password"
    }
]
```

### 2captcha_key.txt
Create `2captcha_key.txt` with your 2captcha API key:
```
YOUR_2CAPTCHA_API_KEY_HERE
```

### proxy.txt (Optional)
Create `proxy.txt` for private proxies (one per line):
```
http://proxy1:port
socks5://proxy2:port
```

### .env (Optional - for point logging)
Create `.env` file for MongoDB connection:
```
# MongoDB Configuration for Point Logging
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# Or for local MongoDB:
# MONGODB_URI=mongodb://localhost:27017/
```

## Usage

### 1. Initial Setup (Generate Tokens)
Run this first to generate access tokens for your accounts:
```bash
python setup.py
```

**Features:**
- **Parallel Processing**: Processes up to 5 accounts simultaneously
- **Captcha Solving**: Automatically solves CloudFlare Turnstile captcha
- **Proxy Support**: Choose from free proxies, private proxies, or no proxy
- **Rate Limiting**: Built-in delays to avoid overwhelming the service

### 2. Run the Bot
After tokens are generated, run the main bot:
```bash
python bot.py
```

**Features:**
- **Automatic Re-setup**: When refresh tokens fail (403 error), automatically re-runs setup for that account
- **Point Logging**: Tracks and logs points to MongoDB (if configured)
- **Mission Automation**: Automatically completes available missions
- **Throughput Monitoring**: Real-time monitoring of account performance
- **Multi-account Support**: Runs all accounts in parallel

## Point Logging System

If you configure MongoDB, the bot will automatically track:

- **Total Requests**: Lifetime request count per account
- **24h Requests**: Daily request statistics  
- **Request Rate**: Current request processing rate
- **Throughput Percentage**: Network performance metrics
- **Mission Rewards**: Automatic mission completion tracking
- **Join Date**: Account registration date
- **Historical Data**: Daily earnings and performance history

### MongoDB Setup

1. **MongoDB Atlas (Cloud - Recommended)**:
   - Create free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Create a new cluster
   - Get connection string and add to `.env` file

2. **Local MongoDB**:
   - Install MongoDB locally
   - Use connection string: `mongodb://localhost:27017/`

## Files Structure

```
├── bot.py              # Main bot script
├── setup.py            # Token setup script  
├── accounts.json       # Account credentials
├── tokens.json         # Generated access tokens (auto-created)
├── 2captcha_key.txt    # 2captcha API key
├── proxy.txt           # Proxy list (optional)
├── .env               # Environment variables (optional)
├── requirements.txt    # Python dependencies
├── ddai_points_tracker.log  # Point logging file (auto-created)
└── README.md          # This file
```

## Enhanced Error Handling

### Automatic Re-setup on 403 Errors
When the bot encounters a 403 error during token refresh (indicating invalid refresh token), it will:

1. Automatically load the account credentials from `accounts.json`
2. Run the setup process for that specific account
3. Solve captcha and generate new tokens
4. Resume normal operation seamlessly

### Parallel Processing Benefits
- **Faster Setup**: Process 5 accounts simultaneously instead of one-by-one
- **Rate Limiting**: Built-in semaphore prevents overwhelming the service
- **Error Isolation**: Failed accounts don't block successful ones

## Troubleshooting

### Common Issues

1. **No tokens generated**:
   - Check your 2captcha API key and balance
   - Verify account credentials in `accounts.json`
   - Check internet connection and proxy settings

2. **403 Refresh Errors**:
   - The bot will automatically handle this by re-running setup
   - Ensure `accounts.json` contains correct credentials
   - Check that 2captcha key is valid

3. **Database connection issues**:
   - Verify MongoDB connection string in `.env`
   - Check MongoDB Atlas whitelist settings
   - Point logging will be disabled if database unavailable

4. **Proxy issues**:
   - Free proxies may be unreliable, consider private proxies
   - Enable proxy rotation for better success rate
   - Bot can run without proxies if needed

### Performance Tips

- Use private proxies for better stability
- Monitor 2captcha balance regularly
- Keep accounts.json secure and backed up
- Check bot logs for performance metrics

## Security Notes

- Keep your `accounts.json` and `2captcha_key.txt` files secure
- Use environment variables for sensitive data
- Consider using a dedicated server for 24/7 operation
- Monitor account activity regularly

## Support

- Check the logs in `ddai_points_tracker.log` for detailed information
- Ensure all dependencies are installed correctly
- Verify network connectivity and proxy settings
- Monitor 2captcha API usage and balance

## License

This bot is for educational purposes. Use responsibly and in accordance with DDAI Network's terms of service.

**vonssy**