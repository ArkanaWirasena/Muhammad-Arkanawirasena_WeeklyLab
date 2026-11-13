from product import Product


class OrderLine:
    def __init__(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("Quantity must be at least 1.")
        self._product: Product = product
        self._quantity: int = quantity

    def get_product(self) -> Product:
        return self._product

    def get_quantity(self) -> int:
        return self._quantity

    def calculate_subtotal(self) -> float:
        return round(self._product.get_price() * self._quantity, 2)

    def display_information(self) -> None:
        print(f"  {self._product.get_id():6} {self._product.get_name():28} "
              f"x {self._quantity:<4} @ ${self._product.get_price():8.2f} "
              f"= ${self.calculate_subtotal():9.2f}")


class Order:
    def __init__(self, order_id: str):
        self._order_id: str = order_id
        self._order_lines: list[OrderLine] = []

    def get_order_id(self) -> str:
        return self._order_id

    def get_order_lines(self) -> tuple[OrderLine, ...]:
        # tuple = read-only view; outside code cannot append/move lines
        return tuple(self._order_lines)

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)   # the Order CREATES the part
        self._order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        for line in self._order_lines:
            if line.get_product().get_id().upper() == product_id.strip().upper():
                self._order_lines.remove(line)        # the part is gone with it
                return True
        return False

    def calculate_total(self) -> float:
        return round(sum(line.calculate_subtotal() for line in self._order_lines), 2)

    def display_order(self) -> None:
        print(f"\nOrder {self._order_id}")
        print("-" * 70)
        if not self._order_lines:
            print("  (no order lines)")
        for line in self._order_lines:
            line.display_information()
        print("-" * 70)
        print(f"  TOTAL: ${self.calculate_total():.2f}")
