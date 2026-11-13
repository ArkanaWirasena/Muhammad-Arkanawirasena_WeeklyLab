from product import Product
from supplier import Supplier
from physical_product import PhysicalProduct
from digital_product import DigitalProduct
from subscription_product import SubscriptionProduct

PRODUCT_TYPES = {
    PhysicalProduct.TYPE: (PhysicalProduct, "Physical Product",
                           [("weight", "weight (kg): ", float)]),
    DigitalProduct.TYPE: (DigitalProduct, "Digital Product",
                          [("download_size", "Download size (MB): ", float)]),
    SubscriptionProduct.TYPE: (SubscriptionProduct, "Subscription Product",
                               [("duration_months", "duration (months): ", int)]),
}

# Used when an old JSON record (Lab 7 format) has no supplier yet
DEFAULT_SUPPLIER_ID = "SUP00"


def get_type_keys() -> list[str]:
    return list(PRODUCT_TYPES.keys())


def get_label(type_key: str) -> str:
    return PRODUCT_TYPES[type_key][1]


def get_extra_fields(type_key: str) -> list[tuple]:
    return PRODUCT_TYPES[type_key][2]


def create_product(type_key: str, product_id: str, name: str,
                   price: float, stock: int, supplier: Supplier, **extra) -> Product:
    if type_key not in PRODUCT_TYPES:
        raise ValueError(f"Invalid product type: {type_key}")
    cls = PRODUCT_TYPES[type_key][0]
    return cls(product_id, name, price, stock, supplier, **extra)


def get_or_create_supplier(data: dict | None, suppliers: dict[str, Supplier]) -> Supplier:
    """Return ONE shared Supplier object per supplier_id."""
    if not data:
        data = {"supplier_id": DEFAULT_SUPPLIER_ID, "name": "Unknown",
                "contact_email": "-"}
    sid = data["supplier_id"]
    if sid not in suppliers:
        suppliers[sid] = Supplier(sid, data["name"], data["contact_email"])
    return suppliers[sid]


def from_dict(item: dict, suppliers: dict[str, Supplier]) -> Product:
    type_key = item.get("type")
    if type_key not in PRODUCT_TYPES:
        raise ValueError(f"Invalid product type: {type_key}")
    supplier = get_or_create_supplier(item.get("supplier"), suppliers)
    extra = {field: conv(item[field]) for field, _, conv in get_extra_fields(type_key)}
    return create_product(type_key, item["id"], item["name"],
                          float(item["price"]), int(item["stock"]), supplier, **extra)