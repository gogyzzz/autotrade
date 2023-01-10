import unittest
from trade_service import TradeService


class TestBuy(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TradeService()

    def test_buy(self):
        result = self.service.buy('NYSE', 'PBR/A', 1000, 8.00)


if __name__ == '__main__':
    unittest.main()
