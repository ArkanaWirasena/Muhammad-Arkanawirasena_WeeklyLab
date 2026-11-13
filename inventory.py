from product import Product


class Inventory:
    """AGGREGATION: an Inventory groups Product objects.

    - Products are created OUTSIDE the inventory and passed in.
    - Removing a product only removes the reference; the Product object
      itself still exists and can be added to another Inventory.
    - The collection is typed with the base class Product, so it can hold
      any subclass (Physical, Digital, Subscription, future types).
    """

    def __init__(self):
        self._products: list[Product] = []

    @property
    def products(self) -> list[Product]:
        # Read-only copy, so outside code cannot change the inventory directly
        return list(self._products)

    def add_product(self, product: Product) -> bool:
        if self.find_product(product.get_id()) is not None:
            print("Product ID already exists.")
            return False
        self._products.append(product)
        print("Product added successfully.")
        return True

    def remove_product(self, product_id: str) -> Product | None:
        """Remove the reference and hand the (still alive) Product back."""
        product = self.find_product(product_id)
        if product is None:
            return None
        self._products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:
        product_id = product_id.strip().upper()
        for p in self._products:
            if p.get_id().upper() == product_id:
                return p
        return None

    def search_product(self, product_id: str) -> Product | None:
        # Kept from earlier labs so older code still works
        return self.find_product(product_id)

    def display_all(self) -> None:
        print("\nCurrent Inventory: ")
        print("-" * 140)
        if not self._products:
            print("Inventory is empty.")
        else:
            # Polymorphism: each object runs its OWN display_information()
            for p in self._products:
                p.display_information()
        print("-" * 140)

    def get_all_products(self) -> list[Product]:
        # used by save/load to convert to JSON
        return list(self._products)

    def clear(self) -> None:
        # Only the references are dropped - the Product objects are not destroyed
        self._products = []