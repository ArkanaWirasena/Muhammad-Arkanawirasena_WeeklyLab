from abc import ABC, abstractmethod
from supplier import Supplier


class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier):
        self._id: str = product_id
        self._name: str = name
        self._price: float = price
        self._stock: int = stock
        self._supplier: Supplier = supplier      # reference only (association)

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_price(self) -> float:
        return self._price

    def get_stock(self) -> int:
        return self._stock

    def get_supplier(self) -> Supplier:
        return self._supplier

    # Behaviour
    def update_stock(self, quantity: int) -> None:
        # Expectation (LSP): any quantity >= 0 is accepted and becomes the new stock;
        # negative quantities are rejected. Subclasses must keep this meaning.
        if quantity < 0:
            print("Stock quantity cannot be negative.")
            return
        self._stock = quantity
        print("Stock updated successfully.")

    def display_information(self) -> None:
        print(f"id: {self._id:6} | name: {self._name:28} | "
              f"price: ${self._price:7.2f} | stock: {self._stock:4} | "
              f"supplier: {self._supplier.get_name():14}", end='')

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "name": self._name,
            "price": self._price,
            "stock": self._stock,
            "supplier": self._supplier.to_dict()
        }

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        """Every concrete product must explain how it is delivered."""
        pass