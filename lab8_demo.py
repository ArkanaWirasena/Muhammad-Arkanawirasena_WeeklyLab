from supplier import Supplier
from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from inventory import Inventory
from order import Order


def heading(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def show_product_details(product: Product) -> None:
    """Accepts ANY Product - used to test substitutability (LSP)."""
    product.display_information()
    print(product.get_fulfilment_info())


# ---------------------------------------------------------------------------
def demo_association() -> tuple[PhysicalProduct, DigitalProduct]:
    heading("2. ASSOCIATION: Supplier <-> Product")
    supplier = Supplier("SUP01", "TechSupply", "sales@techsupply.com")
    laptop = PhysicalProduct("P001", "Laptop", 120.0, 15, supplier, 2.0)
    antivirus = DigitalProduct("D001", "Antivirus", 59.9, 100, supplier, 350.0)

    print("Supplier through each product:")
    laptop.get_supplier().display_information()
    antivirus.get_supplier().display_information()

    print(f"\nSame Supplier object shared by both products? "
          f"{laptop.get_supplier() is antivirus.get_supplier()}")
    print(f"Supplier is a separate object from the product? "
          f"{laptop.get_supplier() is not laptop}")

    print("\n>>> PREDICT FIRST: del supplier, then display supplier through products")
    del supplier
    laptop.get_supplier().display_information()
    antivirus.get_supplier().display_information()
    print("Still works: 'del' only removed the NAME 'supplier'. Each Product still holds")
    print("its own reference, so the Supplier object is still alive.")
    return laptop, antivirus


# ---------------------------------------------------------------------------
def demo_aggregation(laptop: PhysicalProduct) -> None:
    heading("3. AGGREGATION: Inventory <>-- Product")
    print("Product created BEFORE any inventory exists:")
    laptop.display_information()

    inventory_a = Inventory()
    inventory_b = Inventory()
    inventory_a.add_product(laptop)
    print(f"In Inventory A? {inventory_a.find_product('P001') is not None}")

    print("\n>>> PREDICT FIRST: will the Product still work after removal from A?")
    removed = inventory_a.remove_product("P001")
    print(f"In Inventory A after removal? {inventory_a.find_product('P001') is not None}")
    print("Product still usable:")
    removed.display_information()
    print(removed.get_fulfilment_info())

    inventory_b.add_product(removed)
    print(f"\nSame object now in Inventory B? {inventory_b.find_product('P001') is laptop}")

    inventory_b.clear()
    print("Inventory B emptied - product still exists:")
    laptop.display_information()


# ---------------------------------------------------------------------------
def demo_composition(laptop: PhysicalProduct, antivirus: DigitalProduct) -> None:
    heading("4. COMPOSITION: Order <*>-- OrderLine")
    order1 = Order("O001")
    order1.add_order_line(laptop, 2)
    order1.add_order_line(antivirus, 3)
    order1.display_order()

    print("\n>>> PREDICT FIRST: same Product in two Orders - how many OrderLines / Products?")
    order2 = Order("O002")
    order2.add_order_line(laptop, 1)
    order2.display_order()

    line_in_o1 = order1.get_order_lines()[0]
    line_in_o2 = order2.get_order_lines()[0]
    print(f"\nOrderLine in O001 id: {id(line_in_o1)}")
    print(f"OrderLine in O002 id: {id(line_in_o2)}")
    print(f"Same OrderLine object?  {line_in_o1 is line_in_o2}   -> 2 separate OrderLines")
    print(f"Same Product object?    {line_in_o1.get_product() is line_in_o2.get_product()}"
          f"    -> only 1 Product (shared reference)")

    print("\nRemoving the laptop line from O001 through the Order:")
    order1.remove_order_line("P001")
    order1.display_order()
    print("Product is unaffected by the removed line:")
    laptop.display_information()


# ---------------------------------------------------------------------------
def demo_lsp_and_polymorphism(laptop: PhysicalProduct, antivirus: DigitalProduct) -> None:
    heading("6. LSP: show_product_details(product: Product)")
    show_product_details(laptop)
    show_product_details(antivirus)

    print("\nupdate_stock() keeps the same meaning for both subclasses:")
    for p in (laptop, antivirus):
        p.update_stock(20)
        print(f"  {p.get_name()} stock is now {p.get_stock()}")

    print("\nDiagnose: a DigitalProduct that refuses update_stock() breaks callers:")

    class BadDigitalProduct(DigitalProduct):
        def update_stock(self, quantity: int) -> None:
            raise NotImplementedError("Digital products have no stock")

    bad = BadDigitalProduct("D999", "Bad Licence", 9.9, 5, laptop.get_supplier(), 10.0)
    try:
        for p in (laptop, bad):          # code written for Product
            p.update_stock(5)
    except NotImplementedError as e:
        print(f"  CRASH -> NotImplementedError: {e}  (LSP violated)")

    heading("7. POLYMORPHISM: one loop over the Product collection")
    inventory = Inventory()
    inventory.add_product(laptop)
    inventory.add_product(antivirus)
    print(">>> PREDICT FIRST: what will get_fulfilment_info() print for each?")
    for product in inventory.products:          # no isinstance(), no separate loops
        product.display_information()
        print("   ", product.get_fulfilment_info())


if __name__ == "__main__":
    laptop, antivirus = demo_association()
    demo_aggregation(laptop)
    demo_composition(laptop, antivirus)
    demo_lsp_and_polymorphism(laptop, antivirus)