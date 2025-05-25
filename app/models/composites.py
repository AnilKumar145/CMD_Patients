from dataclasses import dataclass

@dataclass
class AddressComposite:
    street: str
    city: str
    state: str
    country: str
    postal_code: str

    def __composite_values__(self):
        return self.street, self.city, self.state, self.country, self.postal_code

    def __eq__(self, other):
        if not isinstance(other, AddressComposite):
            return NotImplemented
        return (
            self.street == other.street
            and self.city == other.city
            and self.state == other.state
            and self.country == other.country
            and self.postal_code == other.postal_code
        )