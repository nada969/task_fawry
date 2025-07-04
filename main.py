from datetime import date , timedelta
from abc import ABC , abstractmethod


class ShippingServicebase(ABC):
    @abstractmethod 
    def getName(self) -> str:
        pass

    def getWeight(self) -> float:
        pass

class Product:
    def __init__(self,name:str,price:float,quantity:int,expiredDate:date=None,weight:float=None):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.expiredDate = expiredDate 
        self.weight = weight
        
    def is_expired(self):
        if self.expiredDate is None:
            return False
        return self.expiredDate < date.today()
    
    def is_shipping(self):
        return self.weight is not None
    
    def get_quantity(self):
        return self.quantity
    
    def update_quantity(self,newQuantity):
        if self.quantity < newQuantity:
            raise ValueError("Can't get quantity by more than the available stock")
        self.quantity -= newQuantity
        return True 

class ShipItem(ShippingServicebase):
    def __init__(self, product:Product,quantity:int):
        self.product = product
        self.quantity = quantity

    def getName(self):
        return self.product.name
    
    def getWeight(self):
        return self.product.weight / 1000


class Customer:
    def __init__(self,name:str,balance:float):
        self.name = name
        self.balance = balance

    def get_name(self):
        return self.name
    
    def get_balance(self):
        return self.balance
    
    def calculate_balance(self,amount:float):
        if self.balance < amount:
            raise ValueError("Customer's balance is insufficient.")
        self.balance -= amount


class Cart:
   
    def __init__(self):
        self.cartItem = [] 

    def add(self,productName:Product,quantity:int):
        if productName.is_expired():
            raise ValueError("This item is expired")
        
        if productName.get_quantity() < quantity:  # Fixed: changed <= to <
            raise ValueError("This item is out of stock")

        self.cartItem.append((productName, quantity))
        

    def is_empty(self):
        return len(self.cartItem) == 0
    
    def get_subtotal(self):
        return sum(product.price * quantity for product, quantity in self.cartItem)
            

class ShippingService:
    ShippingPerKG = 10  # $10 per kg
    
    @staticmethod
    def calculate_shipping_fee(items:list[ShippingServicebase]) -> float:
        total_weight = sum(item.getWeight() for item in items)
        return total_weight * ShippingService.ShippingPerKG
    
    @staticmethod
    def process_shipment(items:list[ShippingServicebase]):
        if not items:
            return
        
        print("** Shipment notice **")
        # Group items by name and calculate total weight
        item_groups = {}
        for item in items:
            name = item.getName()
            if name not in item_groups:
                item_groups[name] = {'count': 0, 'weight': 0}
            item_groups[name]['count'] += 1
            item_groups[name]['weight'] += item.getWeight()
        
        total_weight = 0
        for name, info in item_groups.items():
            weight_per_item = info['weight'] / info['count']
            print(f"{info['count']}x {name} {int(weight_per_item * 1000)}g")
            total_weight += info['weight']
        
        print(f"Total package weight {total_weight}kg")



def checkout(customer:Customer,cart:Cart):

    try:
            
        if cart is None:
            raise ValueError("Cart is Empty")
        
        shippable_items = []
        
        for product, quantity in cart.cartItem:
            # Check if product is expired
            if product.is_expired():
                raise ValueError(f"Product {product.name} has expired")
            
            # Check if product is out of stock
            if quantity > product.get_quantity():
                raise ValueError(f"Product {product.name} is out of stock")
            
            # Collect shippable items
            if product.is_shipping():  # Fixed: changed requires_shipping() to is_shipping()
                for _ in range(quantity):
                    shippable_items.append(ShipItem(product, 1))  # Fixed: changed shippable_items to ShipItem
        
        # Calculate totals
        subtotal = cart.get_subtotal()
        shipping_fee = ShippingService.calculate_shipping_fee(shippable_items)
        total_amount = subtotal + shipping_fee
        
        # Check customer balance
        if customer.get_balance() < total_amount:
            raise ValueError("Customer's balance is insufficient")
        
        # Process shipment if needed
        if shippable_items:
            ShippingService.process_shipment(shippable_items)
        
        # Process payment and update stock
        customer.calculate_balance(total_amount)
        # for product, quantity in cart.cartItem:
        #     product.update_quantity(quantity)
        
        # Print checkout receipt
        print("** Checkout receipt **")
        for product, quantity in cart.cartItem:  # Fixed: changed cart.items to cart.cartItem
            print(f"{quantity}x {product.name} {int(product.price * quantity)}")
        print("----------------------")
        print(f"Subtotal {int(subtotal)}")
        print(f"Shipping {int(shipping_fee)}")
        print(f"Amount {int(total_amount)}")
        print(f"Customer balance after payment: ${customer.get_balance()}")
        print("END.")
        
    except Exception as e:
        print(f"Checkout failed: {e}")



def main():

    print("E-Commerce System Test\n")
    
    # Create products
    cheese = Product("Cheese", 100, 10, date.today() + timedelta(days=7), 200)
    biscuits = Product("Biscuits", 150, 5, date.today() + timedelta(days=30), 700)
    tv = Product("TV", 500, 3,None, 15000)
    scratchCard = Product("Mobile Scratch Card", 50, 100)
    customer = Customer('Ali',0)
    cart = Cart()
    print("Test Case: Following PDF example")
    cart.add(cheese, 2)
    cart.add(tv, 3)  # This will fail - not enough TV stock
    cart.add(scratchCard, 1)
    
    checkout(customer, cart)
    
    print("\n" + "="*50 + "\n")
    
    # Test case that should work
    print("Test Case: Working example")
    customer2 = Customer('John', 2000)
    cart2 = Cart()
    
    cart2.add(cheese, 2)
    cart2.add(biscuits, 1)
    cart2.add(scratchCard, 1)
    
    checkout(customer2, cart2)
    
    print("\n" + "="*50 + "\n")
    
    # Test insufficient balance
    print("Test Case: Insufficient balance")
    poor_customer = Customer('Poor Customer', 50)
    cart3 = Cart()
    cart3.add(cheese, 2)
    checkout(poor_customer, cart3)
    
    print("\n" + "="*50 + "\n")
    
    # Test expired product
    print("Test Case: Expired product")
    expired_milk = Product("Expired Milk", 80, 5, date.today() - timedelta(days=1), 500)
    cart4 = Cart()
    try:
        cart4.add(expired_milk, 1)
    except Exception as e:
        print(f"Add to cart failed: {e}")

if __name__ == "__main__":
    main()