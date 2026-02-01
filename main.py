import argparse
import json
import sys
from stake_validator import StakeValidator


def main():
    parser = argparse.ArgumentParser(
        description="Stake.com - Account Validator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage example:
  python main.py --token YOUR_TOKEN_HERE
  python main.py -t YOUR_TOKEN_HERE
        """
    )
    
    parser.add_argument(
        "-t", "--token",
        type=str,
        required=True,
        help="Stake.com session token"
    )
    
    args = parser.parse_args()
    
    if not args.token:
        error_response = {
            "success": False,
            "error": "Token not provided"
        }
        print(json.dumps(error_response, indent=2, ensure_ascii=False))
        sys.exit(1)
    
    validator = StakeValidator(args.token)
    results = validator.get_all_data()
    
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
