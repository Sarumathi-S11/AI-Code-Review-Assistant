"""Small example of readable, documented Python code."""

TAX_RATE = 0.08

def calculate_total(price: float, quantity: int) -> float:
    """Return the total price including tax."""
    subtotal = price * quantity
    return subtotal * (1 + TAX_RATE)

class Invoice:
    """Represent a simple invoice."""

    def __init__(self, customer: str):
        """Initialize an invoice for a customer."""
        self.customer = customer
