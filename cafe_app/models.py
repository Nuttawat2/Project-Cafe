from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True, db_column='Customer_ID')
    first_name = models.CharField(max_length=100, db_column='First_Name')
    last_name = models.CharField(max_length=100, db_column='Last_Name')
    phone = models.CharField(max_length=15, blank=True, null=True, db_column='Phone')
    email = models.CharField(max_length=150, blank=True, null=True, db_column='Email')
    created_at = models.DateTimeField(auto_now_add=True, db_column='Created_At')

    class Meta:
        managed = False
        db_table = 'CUSTOMER'

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True, db_column='Employee_ID')
    first_name = models.CharField(max_length=100, db_column='First_Name')
    last_name = models.CharField(max_length=100, db_column='Last_Name')
    position = models.CharField(max_length=50, blank=True, null=True, db_column='Position')
    phone = models.CharField(max_length=15, blank=True, null=True, db_column='Phone')
    hire_date = models.DateField(auto_now_add=True, db_column='Hire_Date')

    class Meta:
        managed = False
        db_table = 'EMPLOYEE'

class MenuItem(models.Model):
    menu_id = models.AutoField(primary_key=True, db_column='Menu_ID')
    name = models.CharField(max_length=150, db_column='Name')
    category = models.CharField(max_length=50, blank=True, null=True, db_column='Category')
    price = models.DecimalField(max_digits=8, decimal_places=2, db_column='Price')
    is_available = models.BooleanField(default=True, db_column='Is_Available')
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True, db_column='Image')

    class Meta:
        managed = False
        db_table = 'MENU_ITEM'

class Ingredient(models.Model):
    ingredient_id = models.AutoField(primary_key=True, db_column='Ingredient_ID')
    name = models.CharField(max_length=150, db_column='Name')
    unit = models.CharField(max_length=30, blank=True, null=True, db_column='Unit')
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Current_Stock')
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Min_Stock')

    class Meta:
        managed = False
        db_table = 'INGREDIENT'

class Order(models.Model):
    order_id = models.AutoField(primary_key=True, db_column='Order_ID')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='Customer_ID')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='Employee_ID')
    order_date = models.DateTimeField(auto_now_add=True, db_column='Order_Date')
    status = models.CharField(max_length=20, default='pending', db_column='Status')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Total_Price')

    class Meta:
        managed = False
        db_table = 'ORDER'

class OrderItem(models.Model):
    orderitem_id = models.AutoField(primary_key=True, db_column='OrderItem_ID')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='Order_ID')
    menu = models.ForeignKey(MenuItem, on_delete=models.CASCADE, db_column='Menu_ID')
    quantity = models.IntegerField(default=1, db_column='Quantity')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, db_column='Subtotal')

    class Meta:
        managed = False
        db_table = 'ORDER_ITEM'

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True, db_column='Recipe_ID')
    menu = models.ForeignKey(MenuItem, on_delete=models.CASCADE, db_column='Menu_ID')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column='Ingredient_ID')
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, db_column='Quantity_Used')
    unit = models.CharField(max_length=30, blank=True, null=True, db_column='Unit')

    class Meta:
        managed = False
        db_table = 'RECIPE'

class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True, db_column='Stock_ID')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, db_column='Ingredient_ID')
    transaction_date = models.DateTimeField(auto_now_add=True, db_column='Transaction_Date')
    transaction_type = models.CharField(max_length=10, db_column='Transaction_Type')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, db_column='Quantity')
    note = models.CharField(max_length=255, blank=True, null=True, db_column='Note')

    class Meta:
        managed = False
        db_table = 'STOCK'

class Queue(models.Model):
    queue_id = models.AutoField(primary_key=True, db_column='Queue_ID')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='Order_ID')
    queue_number = models.IntegerField(db_column='Queue_Number')
    status = models.CharField(max_length=20, default='waiting', db_column='Status')
    created_at = models.DateTimeField(auto_now_add=True, db_column='Created_At')

    class Meta:
        managed = False
        db_table = 'QUEUE'

class Promotion(models.Model):
    promotion_id = models.AutoField(primary_key=True, db_column='Promotion_ID')
    name = models.CharField(max_length=150, db_column='Name')
    description = models.CharField(max_length=255, blank=True, null=True, db_column='Description')
    discount_type = models.CharField(max_length=20, db_column='Discount_Type')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, db_column='Discount_Value')
    start_date = models.DateField(db_column='Start_Date')
    end_date = models.DateField(db_column='End_Date')
    is_active = models.BooleanField(default=True, db_column='Is_Active')

    class Meta:
        managed = False
        db_table = 'PROMOTION'

class LoyaltyPoint(models.Model):
    point_id = models.AutoField(primary_key=True, db_column='Point_ID')
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, db_column='Customer_ID')
    points = models.IntegerField(default=0, db_column='Points')
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Total_Spent')
    updated_at = models.DateTimeField(auto_now=True, db_column='Updated_At')

    class Meta:
        managed = False
        db_table = 'LOYALTY_POINT'