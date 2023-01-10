def parse_account(account: str):
    account_number, account_product_code = account.split('-')
    assert len(account_number) == 8
    assert len(account_product_code) == 2

    return account_number, account_product_code


def parse_oversea_stock(code: str):
    exchange, ticker = code.split(':')
    assert exchange == "NASD" or exchange == "NYSE" or exchange == "NAS" or exchange == "NYS"

    return exchange, ticker
