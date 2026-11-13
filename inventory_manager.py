import os
import json
from inventory import Inventory
from product import Product
from supplier import Supplier
from order import Order
from can_be_shipped import CanBeShipped
import product_factory

#File handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTORY_FILE = os.path.join(SCRIPT_DIR, "inventory.json")


def load_inventory(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    if not os.path.exists(INVENTORY_FILE):
        print("inventory.json not found")
        return

    try:
        with open(INVENTORY_FILE, "r") as f:
            data = json.load(f)

        inventory.clear()
        for item in data:
            try:
                inventory.add_product(product_factory.from_dict(item, suppliers))
            except (KeyError, ValueError, TypeError) as e:
                print(f"Skipped invalid record {item.get('id','?')}: {e}")

        print("inventory.json found")
        print("Inventory loaded successfully")
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading inventory.json: {e}")


def save_inventory(inventory: Inventory) -> None:
    data = [p.to_dict() for p in inventory.get_all_products()]

    try:
        with open(INVENTORY_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print("Inventory saved to inventory.json.")
    except IOError as e:
        print(f"Error saving inventory: {e}")


def display_all(inventory: Inventory) -> None:
    inventory.display_all()


def choose_product_type() -> str | None:
    keys = product_factory.get_type_keys()
    print("Product type:")
    for i, key in enumerate(keys, start=1):
        print(f"{i}. {product_factory.get_label(key)}")
    choice = input(f"Choose product type (1-{len(keys)}): ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(keys)):
        return None
    return keys[int(choice) - 1]


def choose_supplier(suppliers: dict[str, Supplier]) -> Supplier | None:
    """Pick an existing Supplier or create a new one (created OUTSIDE Product)."""
    if suppliers:
        print("Existing suppliers:")
        for s in suppliers.values():
            print(f"  {s.get_supplier_id()} - {s.get_name()}")
    supplier_id = input("Supplier ID (existing or new): ").strip().upper()
    if not supplier_id:
        return None
    if supplier_id in suppliers:
        return suppliers[supplier_id]

    name = input("New supplier name: ").strip()
    email = input("New supplier contact email: ").strip()
    if not name or not email:
        return None
    supplier = Supplier(supplier_id, name, email)
    suppliers[supplier_id] = supplier
    return supplier


def add_product(inventory: Inventory, suppliers: dict[str, Supplier]) -> None:
    print("\nAdd New Product")
    type_key = choose_product_type()
    if type_key is None:
        print("Invalid product type.")
        return

    product_id = input("Product ID: ").strip()
    name = input("Product Name: ").strip()
    if not product_id or not name:
        print("Product ID and Name cannot be empty.")
        return

    try:
        price = float(input("Product Price: "))
        stock = int(input("Stock Quantity: "))
        extra = {field: conv(input(prompt))
                 for field, prompt, conv in product_factory.get_extra_fields(type_key)}
        if price < 0 or stock < 0:
            raise ValueError("Price and stock cannot be negative.")
    except ValueError as e:
        print(f"Invalid input: {e}")
        return

    supplier = choose_supplier(suppliers)
    if supplier is None:
        print("A valid supplier is required.")
        return

    try:
        product = product_factory.create_product(type_key, product_id, name,
                                                 price, stock, supplier, **extra)
    except ValueError as e:
        print(f"Invalid input: {e}")
        return

    inventory.add_product(product)


def update_stock(inventory: Inventory) -> None:
    print("\nUpdate Stock")
    item = inventory.find_product(input("Enter Product ID: "))

    if item is None:
        print("Product not found.")
        return

    try:
        new_stock = int(input("Enter new stock quantity: "))
    except ValueError:
        print("Invalid stock quantity.")
        return

    item.update_stock(new_stock)   # Product prints its own success/error message


def show_product_details(product: Product) -> None:
    """Works for ANY Product subclass - no isinstance() needed (LSP + polymorphism)."""
    product.display_information()
    print(f"Fulfilment Info: {product.get_fulfilment_info()}")
    print("Supplied by: ", end="")
    product.get_supplier().display_information()


def search_product(inventory: Inventory) -> None:
    print("\nSearch Product")
    item = inventory.find_product(input("Enter Product ID to search: "))

    if item is None:
        print("Product not found.")
        return

    print("\nProduct found:")
    print("-" * 140)
    show_product_details(item)
    # Only objects that signed the CanBeShipped contract have a shipping cost
    if isinstance(item, CanBeShipped):
        print(f"Shipping Cost: ${item.calculate_shipping_cost():.2f}")
    print("-" * 140)


def remove_product(inventory: Inventory) -> None:
    print("\nRemove Product")
    removed = inventory.remove_product(input("Enter Product ID to remove: "))
    if removed is None:
        print("Product not found.")
        return
    # Aggregation: the reference is removed, the Product object still exists
    print(f"Removed '{removed.get_name()}' from the inventory "
          f"(the product object still exists and could be added elsewhere).")


def create_order(inventory: Inventory, orders: list[Order]) -> None:
    print("\nCreate Order")
    order_id = input("Order ID: ").strip()
    if not order_id:
        print("Order ID cannot be empty.")
        return

    order = Order(order_id)
    while True:
        product_id = input("Product ID to add (blank to finish): ").strip()
        if not product_id:
            break
        product = inventory.find_product(product_id)
        if product is None:
            print("Product not found.")
            continue
        try:
            quantity = int(input("Quantity: "))
            order.add_order_line(product, quantity)   # Order creates the OrderLine
            print("Line added.")
        except ValueError as e:
            print(f"Invalid quantity: {e}")

    if not order.get_order_lines():
        print("Order has no lines - not created.")
        return
    orders.append(order)
    order.display_order()


def view_orders(orders: list[Order]) -> None:
    if not orders:
        print("\nNo orders yet.")
        return
    for order in orders:
        order.display_order()


def menu() -> None:
    print("----------MENU----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Remove Product")
    print("6. Create Order")
    print("7. View Orders")
    print("8. Save Inventory")
    print("9. Exit")
    print("------------------------")


def main() -> None:
    print("====================================")
    print("INVENTORY MANAGEMENT SYSTEM")
    print("====================================")
    inventory = Inventory()
    suppliers: dict[str, Supplier] = {}
    orders: list[Order] = []
    load_inventory(inventory, suppliers)

    while True:
        menu()
        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            display_all(inventory)
        elif choice == "2":
            add_product(inventory, suppliers)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            remove_product(inventory)
        elif choice == "6":
            create_order(inventory, orders)
        elif choice == "7":
            view_orders(orders)
        elif choice == "8":
            save_inventory(inventory)
        elif choice == "9":
            if input("Save before exiting? (y/n): ").strip().lower() == "y":
                save_inventory(inventory)
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please enter 1-9")

        input("\nPress Enter to continue")

if __name__ == "__main__":
    main()
