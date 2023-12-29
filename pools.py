from solders.pubkey import Pubkey
from solders.instruction import Instruction

from solana.transaction import AccountMeta

from layouts import POOL_INFO_LAYOUT

import json, requests

AMM_PROGRAM_ID = Pubkey.from_string('675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8')

def make_simulate_pool_info_instruction(accounts):

        keys = [
            AccountMeta(pubkey=accounts["amm_id"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["authority"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["open_orders"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["base_vault"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["quote_vault"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["lp_mint"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["market_id"], is_signer=False, is_writable=False),    
            AccountMeta(pubkey=accounts['event_queue'], is_signer=False, is_writable=False),    
            
            
        ]
        data = POOL_INFO_LAYOUT.build(
            dict(
                instruction=12,
                simulate_type=0
            )
        )
        return Instruction(AMM_PROGRAM_ID, data, keys)


def extract_pool_info(pools_list: list, mint: str) -> dict:
    quoteTokens = ["So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"]
    for pool in pools_list:
        if pool['baseMint'] == mint and pool['quoteMint'] in quoteTokens:
            return pool
        
    raise Exception(f'{mint} pool not found!')


def fetch_pool_keys(mint: str):
    amm_info = {}
    all_pools = {}
    try:
        # Using this so it will be faster else no option, we go the slower way.
        with open('all_pools.json', 'r') as file:
            all_pools = json.load(file)
        amm_info = extract_pool_info(all_pools, mint)
    except:
        resp = requests.get('https://api.raydium.io/v2/sdk/liquidity/mainnet.json', stream=True)
        pools = resp.json()
        official = pools['official']
        unofficial = pools['unOfficial'] 
        all_pools = official + unofficial

        # Store all_pools in a JSON file
        with open('all_pools.json', 'w') as file:
            json.dump(all_pools, file, default=lambda x: x.__dict__)
        amm_info = extract_pool_info(all_pools, mint)

    return {
        'amm_id': Pubkey.from_string(amm_info['id']),
        'authority': Pubkey.from_string(amm_info['authority']),
        'base_mint': Pubkey.from_string(amm_info['baseMint']),
        'base_decimals': amm_info['baseDecimals'],
        'quote_mint': Pubkey.from_string(amm_info['quoteMint']),
        'quote_decimals': amm_info['quoteDecimals'],
        'lp_mint': Pubkey.from_string(amm_info['lpMint']),
        'open_orders': Pubkey.from_string(amm_info['openOrders']),
        'target_orders': Pubkey.from_string(amm_info['targetOrders']),
        'base_vault': Pubkey.from_string(amm_info['baseVault']),
        'quote_vault': Pubkey.from_string(amm_info['quoteVault']),
        'market_id': Pubkey.from_string(amm_info['marketId']),
        'market_base_vault': Pubkey.from_string(amm_info['marketBaseVault']),
        'market_quote_vault': Pubkey.from_string(amm_info['marketQuoteVault']),
        'market_authority': Pubkey.from_string(amm_info['marketAuthority']),
        'bids': Pubkey.from_string(amm_info['marketBids']),
        'asks': Pubkey.from_string(amm_info['marketAsks']),
        'event_queue': Pubkey.from_string(amm_info['marketEventQueue'])
    }
