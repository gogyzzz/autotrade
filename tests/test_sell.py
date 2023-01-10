import unittest
from trade_service import TradeService


class TestSell(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TradeService()

    def test_sell(self):
        result = self.service.sell('NYSE', 'PBR/A', 1, 8.8)
        pass


if __name__ == '__main__':
    unittest.main()
