from product import Product
from supplier import Supplier


class SubscriptionProduct(Product):
    TYPE = "subscription"

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, duration_months: int):
        super().__init__(product_id, name, price, stock, supplier)
        if duration_months <= 0:
            raise ValueError("Duration must be at least 1 month.")
        self._duration_months: int = duration_months

    def get_duration_months(self) -> int:
        return self._duration_months

    def display_information(self) -> None:
        super().display_information()
        print(f" | type: Subscription | Duration: {self._duration_months} months")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = self.TYPE
        data["duration_months"] = self._duration_months
        return data

    def get_fulfilment_info(self) -> str:
        return f"'{self._name}' subscription will be activated for {self._duration_months} months."