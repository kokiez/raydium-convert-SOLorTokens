

from solana.rpc.commitment import Commitment
from solana.rpc.api import Client
from solana.transaction import Transaction

from solders.keypair import Keypair

from pools import  fetch_pool_keys, make_simulate_pool_info_instruction
import re
from ast import literal_eval


LIQUIDITY_FEES_NUMERATOR = 25
LIQUIDITY_FEES_DENOMINATOR = 10000

"""
Required Variables
"""
endpoint = "your_rpc_url"
payer = Keypair.from_base58_string("your_private_key")
token = "ca of your mint/mint address"
solana_client = Client(endpoint, commitment=Commitment("confirmed"), blockhash_cache=True)


def calculateAmountOut(amount, pool_info):
    status = pool_info['status']
    SWAP_decimals = pool_info['coin_decimals'] #swap coin
    SOL_decimals = pool_info['pc_decimals'] #SOL
    COIN_lp_decimals = pool_info['lp_decimals'] #swap coin
    pool_SOL_amount = pool_info['pool_pc_amount'] #sol
    pool_SWAP_amount = pool_info['pool_coin_amount'] #coin
    Coin_pool_lp_supply =  pool_info['pool_lp_supply'] #coin


    reserve_in = pool_SOL_amount
    reserve_out = pool_SWAP_amount

    current_price = reserve_out / reserve_in
    # print(f"Current Price in SOL: {current_price:.12f}")

    amount_in = amount * 10 ** SOL_decimals
    Fees = (amount_in * LIQUIDITY_FEES_NUMERATOR)/LIQUIDITY_FEES_DENOMINATOR
    amount_in_with_fee = amount_in - Fees
    amountOutRaw = (reserve_out * amount_in_with_fee) / (reserve_in + amount_in_with_fee)
    # Slippage = 1 + slippage
    # minimumAmountOut = amountOutRaw / slippage
    return amountOutRaw / 10 ** SWAP_decimals



def calculateAmountIn(amount, pool_info):
    SWAP_decimals = pool_info['coin_decimals'] #swap coin
    SOL_decimals = pool_info['pc_decimals'] #SOL
    COIN_lp_decimals = pool_info['lp_decimals'] #swap coin
    pool_SOL_amount = pool_info['pool_pc_amount'] #sol
    pool_SWAP_amount = pool_info['pool_coin_amount'] #coin
    Coin_pool_lp_supply =  pool_info['pool_lp_supply'] #coin


    reserve_in = pool_SWAP_amount
    reserve_out = pool_SOL_amount

    current_price = reserve_out / reserve_in
    # print(f"Current Price in SOL: {current_price:.12f}")

    amount_in = amount * 10 ** SWAP_decimals
    Fees = (amount_in * LIQUIDITY_FEES_NUMERATOR)/LIQUIDITY_FEES_DENOMINATOR
    amount_in_with_fee = amount_in - Fees
    amountOutRaw = (reserve_out * amount_in_with_fee) / (reserve_in + amount_in_with_fee)
    # Slippage = 1 + slippage
    # minimumAmountOut = amountOutRaw / slippage
    return amountOutRaw / 10 ** SOL_decimals



def PoolInfo(mint):
    while True:
        quote = ""
        pool_keys = fetch_pool_keys(mint)
        if str(pool_keys['quote_mint']) == "So11111111111111111111111111111111111111112":
            quote = "SOL"
        elif str(pool_keys['quote_mint']) == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":
            quote = "USDC"
        elif str(pool_keys['quote_mint']) == "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB":
            quote = "USDC"

        recent_block_hash = solana_client.get_latest_blockhash().value.blockhash
        tx = Transaction(recent_blockhash=recent_block_hash, fee_payer=payer.pubkey())
        sim_inst = make_simulate_pool_info_instruction(pool_keys)
        tx.add(sim_inst)
        signers = [payer]
        tx.sign(*signers)
        res = None
        response = solana_client.simulate_transaction(tx).value.logs
        
        for log in response:
            if 'Program log: GetPoolData:' in log:
                res = log
                break
        if res != None:
            return res, quote



# Get pool info
res, quote_type = PoolInfo(token)
# Extract the pool info from response
pool_info = literal_eval(re.search('({.+})', res).group(0))


# Compute Input and Output
amountInSOL = 0.1
if quote_type == "SOL":
    mint = calculateAmountOut(amountInSOL,pool_info)
    print("Raydium Output Tokens:",mint)

    sol = calculateAmountIn(mint, pool_info)
    print("Raydium Output SOL:",sol)

else:
#because there are no pairs with SOL, its SOL/USDT not USDT/SOL
    mint = calculateAmountIn(amountInSOL,pool_info)
    print("Raydium Output Tokens:",mint)

    sol = calculateAmountOut(mint, pool_info)
    print("Raydium Output SOL:",sol)