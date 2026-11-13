"""Lab 8 tests (section 9 checklist).  Run:  python -m unittest test_lab8.py -v"""
import inspect
import json
import os
import tempfile
import unittest
from typing import get_type_hints

import inventory_manager
from supplier import Supplier
from product import Product
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from subscription_product import SubscriptionProduct
from inventory import Inventory
from order import Order, OrderLine


def make_products():
    supplier = Supplier("SUP01", "TechSupply", "sales@techsupply.com")
    laptop = PhysicalProduct("P001", "Laptop", 120.0, 15, supplier, 2.0)
    antivirus = DigitalProduct("D001", "Antivirus", 59.9, 100, supplier, 350.0)
    return supplier, laptop, antivirus


class TestAssociation(unittest.TestCase):
    def test_product_stores_supplier_reference(self):
        supplier, laptop, antivirus = make_products()
        self.assertIs(laptop.get_supplier(), supplier)
        self.assertIs(antivirus.get_supplier(), supplier)

    def test_supplier_and_product_independent(self):
        supplier, laptop, _ = make_products()
        del supplier                                    # name gone, object alive
        self.assertEqual(laptop.get_supplier().get_name(), "TechSupply")
        lone_supplier = Supplier("SUP09", "Solo", "solo@x.com")   # no products needed
        self.assertEqual(lone_supplier.get_name(), "Solo")


class TestAggregation(unittest.TestCase):
    def test_transfer_between_inventories(self):
        _, laptop, _ = make_products()
        inv_a, inv_b = Inventory(), Inventory()
        inv_a.add_product(laptop)
        removed = inv_a.remove_product("P001")
        self.assertIs(removed, laptop)
        self.assertIsNone(inv_a.find_product("P001"))
        self.assertEqual(laptop.get_name(), "Laptop")   # still usable
        inv_b.add_product(laptop)
        self.assertIs(inv_b.find_product("P001"), laptop)

    def test_clear_does_not_destroy_products(self):
        _, laptop, _ = make_products()
        inv = Inventory()
        inv.add_product(laptop)
        inv.clear()
        self.assertEqual(laptop.get_price(), 120.0)

    def test_remove_missing_returns_none(self):
        self.assertIsNone(Inventory().remove_product("NOPE"))


class TestComposition(unittest.TestCase):
    def test_order_creates_its_own_lines(self):
        _, laptop, antivirus = make_products()
        order = Order("O001")
        order.add_order_line(laptop, 2)
        order.add_order_line(antivirus, 3)
        lines = order.get_order_lines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(isinstance(l, OrderLine) for l in lines))
        self.assertAlmostEqual(order.calculate_total(), 240.0 + 179.7)

    def test_same_product_two_orders(self):
        _, laptop, _ = make_products()
        o1, o2 = Order("O1"), Order("O2")
        o1.add_order_line(laptop, 1)
        o2.add_order_line(laptop, 1)
        self.assertIsNot(o1.get_order_lines()[0], o2.get_order_lines()[0])
        self.assertIs(o1.get_order_lines()[0].get_product(), laptop)

    def test_lines_cannot_be_added_from_outside(self):
        _, laptop, _ = make_products()
        order = Order("O1")
        order.add_order_line(laptop, 1)
        self.assertIsInstance(order.get_order_lines(), tuple)   # read-only view

    def test_remove_line_through_order(self):
        _, laptop, _ = make_products()
        order = Order("O1")
        order.add_order_line(laptop, 1)
        self.assertTrue(order.remove_order_line("P001"))
        self.assertEqual(order.calculate_total(), 0)
        self.assertEqual(laptop.get_stock(), 15)          # product not affected


class TestTypeHints(unittest.TestCase):
    def test_key_hints_present(self):
        self.assertIs(get_type_hints(Product.__init__)["supplier"], Supplier)
        self.assertEqual(get_type_hints(Inventory.find_product)["return"], Product | None)
        self.assertIs(get_type_hints(Order.add_order_line)["product"], Product)
        self.assertIs(get_type_hints(OrderLine.calculate_subtotal)["return"], float)
        src = inspect.getsource(Inventory.__init__)
        self.assertIn("list[Product]", src)
        self.assertIn("list[OrderLine]", inspect.getsource(Order.__init__))


class TestLSPAndPolymorphism(unittest.TestCase):
    def test_subclasses_substitute_for_product(self):
        supplier, laptop, antivirus = make_products()
        cloud = SubscriptionProduct("S1", "Cloud", 9.9, 5, supplier, 12)
        inv = Inventory()
        for p in (laptop, antivirus, cloud):
            self.assertIsInstance(p, Product)
            inv.add_product(p)
        infos = [p.get_fulfilment_info() for p in inv.products]   # one loop
        self.assertIn("shipped", infos[0])
        self.assertIn("digitally", infos[1])
        self.assertIn("activated", infos[2])

    def test_update_stock_same_meaning(self):
        _, laptop, antivirus = make_products()
        for p in (laptop, antivirus):
            p.update_stock(7)
            self.assertEqual(p.get_stock(), 7)
            p.update_stock(-1)                       # rejected the same way
            self.assertEqual(p.get_stock(), 7)


class TestPersistence(unittest.TestCase):
    def test_save_load_keeps_types_and_shared_supplier(self):
        tmp = tempfile.mkdtemp()
        original = inventory_manager.INVENTORY_FILE
        inventory_manager.INVENTORY_FILE = os.path.join(tmp, "inventory.json")
        try:
            _, laptop, antivirus = make_products()
            inv = Inventory()
            inv.add_product(laptop)
            inv.add_product(antivirus)
            inventory_manager.save_inventory(inv)

            restored, suppliers = Inventory(), {}
            inventory_manager.load_inventory(restored, suppliers)
            p, d = restored.find_product("P001"), restored.find_product("D001")
            self.assertIsInstance(p, PhysicalProduct)
            self.assertIsInstance(d, DigitalProduct)
            self.assertIs(p.get_supplier(), d.get_supplier())   # one shared Supplier
            self.assertEqual(len(suppliers), 1)
        finally:
            inventory_manager.INVENTORY_FILE = original


if __name__ == "__main__":
    unittest.main(verbosity=2)