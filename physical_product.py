from product import Product
from supplier import Supplier
from can_be_shipped import CanBeShipped


class PhysicalProduct(Product, CanBeShipped):
    TYPE = "physical"
    BASE_SHIPPING_FEE = 5.00
    RATE_PER_KG = 2.00

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float):
        super().__init__(product_id, name, price, stock, supplier)
        if weight < 0:
            raise ValueError("Weight cannot be negative.")
        self._weight: float = weight

    def get_weight(self) -> float:
        return self._weight

    def display_information(self) -> None:
        super().display_information()
        print(f" | type: Physical     | Weight: {self._weight:.2f} kg")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = self.TYPE
        data["weight"] = self._weight
        return data

    # Abstract method from Product
    def get_fulfilment_info(self) -> str:
        return f"'{self._name}' will be shipped to the customer's address."

    # Interface method from CanBeShipped
    def calculate_shipping_cost(self) -> float:
        return round(self.BASE_SHIPPING_FEE + (self.RATE_PER_KG * self._weight), 2)