from product import Product
from supplier import Supplier


class DigitalProduct(Product):
    TYPE = "digital"

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float):
        super().__init__(product_id, name, price, stock, supplier)
        if download_size <= 0:
            raise ValueError("Download size must be positive.")
        self._download_size: float = download_size

    def get_download_size(self) -> float:
        return self._download_size

    def display_information(self) -> None:
        super().display_information()
        print(f" | type: Digital      | Download Size: {self._download_size:.1f} MB")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = self.TYPE
        data["download_size"] = self._download_size
        return data

    def get_fulfilment_info(self) -> str:
        return f"'{self._name}' is delivered digitally via download link."

    # NOTE (LSP): update_stock() is NOT overridden, so a DigitalProduct keeps
    # the same meaning as Product and can stand in for it anywhere.