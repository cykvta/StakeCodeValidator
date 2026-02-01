# Stake Code Validator

Tool to validate and retrieve Stake.com account information through its GraphQL API.

## Requirements

- Python 3.8+
- Dependencies in `requirements.txt`

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py -t <TOKEN>
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `-t`, `--token` | Stake.com session token (required) |

### Example

```bash
python main.py -t abc123def456...
```

## Response

The response is in JSON format with the following structure:

```json
{
  "success": true,
  "timestamp": "2026-02-01T12:00:00.000000",
  "username": "user",
  "data": {
    "welcome_offer": {
      "signup_code": "DRAKE",
      "affiliate_deal_type": "wagerShare"
    },
    "wallets": [
      {
        "currency": "BTC",
        "address": "bc1q..."
      },
      {
        "currency": "ETH",
        "address": "0x..."
      }
    ]
  },
  "error": null
}
```

## Retrieved Data

| Field | Description |
|-------|-------------|
| `username` | Stake username |
| `welcome_offer.signup_code` | Streamer/affiliate code used at registration (e.g., DRAKE, TRAINWRECK, XPOSED) |
| `welcome_offer.affiliate_deal_type` | Affiliate deal type (wagerShare, etc.) |
| `wallets` | List of wallets with deposit address |

### Supported Wallets

- BTC, ETH, LTC, DOGE, BCH
- XRP, TRX, EOS, BNB
- USDT, USDC, BUSD
- SOL, POL, LINK, UNI, SHIB, APE

## Logs

Events and errors are logged to `logs.txt` with the following format:

```
2026-02-01 12:00:00,000 - INFO - Message
2026-02-01 12:00:00,000 - ERROR - Error
```

## Project Structure

```
StakeCodeValidator/
├── main.py              # Entry point
├── stake_validator.py   # Main class
├── requirements.txt     # Dependencies
├── logs.txt            # Log file
├── .gitignore          # Ignored files
└── README.md           # Documentation
```

## License

MIT
