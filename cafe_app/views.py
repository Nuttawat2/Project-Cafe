from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .models import MenuItem, Ingredient

@login_required
def dashboard(request):
    today = date.today()
    total_menus = MenuItem.objects.count()
    total_ingredients = Ingredient.objects.count()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*), ISNULL(SUM(Total_Price), 0)
            FROM [ORDER]
            WHERE CAST(Order_Date AS DATE) = %s
        """, [today])
        row = cursor.fetchone()
        today_orders = row[0]
        today_revenue = row[1]

        cursor.execute("""
            SELECT TOP 5
                C.First_Name + ' ' + C.Last_Name AS Customer_Name,
                O.Total_Price,
                O.Status,
                O.Order_Date
            FROM [ORDER] O
            JOIN CUSTOMER C ON O.Customer_ID = C.Customer_ID
            ORDER BY O.Order_Date DESC
        """)
        recent_orders = cursor.fetchall()

        cursor.execute("""
            SELECT Name, Current_Stock, Min_Stock, Unit
            FROM INGREDIENT
            WHERE Current_Stock <= Min_Stock
        """)
        low_stock = cursor.fetchall()

    return render(request, 'cafe_app/dashboard.html', {
        'total_menus': total_menus,
        'total_ingredients': total_ingredients,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
    })

@login_required
def menu_list(request):
    menus = MenuItem.objects.all()
    return render(request, 'cafe_app/menu_list.html', {'menus': menus})

@login_required
def menu_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        is_available = request.POST.get('is_available') == 'on'
        image = request.FILES.get('image')
        menu = MenuItem(
            name=name,
            category=category,
            price=price,
            is_available=is_available,
            image=image
        )
        menu.save()
        messages.success(request, 'เพิ่มเมนูเรียบร้อยแล้ว')
        return redirect('menu_list')
    return render(request, 'cafe_app/menu_form.html', {'action': 'เพิ่มเมนู'})

@login_required
def menu_edit(request, pk):
    menu = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        menu.name = request.POST.get('name')
        menu.category = request.POST.get('category')
        menu.price = request.POST.get('price')
        menu.is_available = request.POST.get('is_available') == 'on'
        if request.FILES.get('image'):
            menu.image = request.FILES.get('image')
        menu.save()
        messages.success(request, 'แก้ไขเมนูเรียบร้อยแล้ว')
        return redirect('menu_list')
    return render(request, 'cafe_app/menu_form.html', {'action': 'แก้ไขเมนู', 'menu': menu})

@login_required
def menu_delete(request, pk):
    menu = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, 'ลบเมนูเรียบร้อยแล้ว')
        return redirect('menu_list')
    return render(request, 'cafe_app/menu_confirm_delete.html', {'menu': menu})

@login_required
def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    low_stock = Ingredient.objects.filter(current_stock__lte=F('min_stock'))
    return render(request, 'cafe_app/ingredient_list.html', {
        'ingredients': ingredients,
        'low_stock_ids': [i.ingredient_id for i in low_stock]
    })

@login_required
def add_stock(request, pk):
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        note = request.POST.get('note', '')
        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC sp_AddStock @Ingredient_ID=%s, @Quantity=%s, @Note=%s",
                [pk, quantity, note]
            )
        messages.success(request, 'เติมสต็อกเรียบร้อยแล้ว')
        return redirect('ingredient_list')
    return render(request, 'cafe_app/add_stock.html', {'ingredient': ingredient})

@login_required
def order_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                O.Order_ID,
                C.Customer_Code,
                C.First_Name + ' ' + C.Last_Name AS Customer_Name,
                E.First_Name + ' ' + E.Last_Name AS Employee_Name,
                O.Order_Date,
                O.Status,
                O.Total_Price
            FROM [ORDER] O
            JOIN CUSTOMER C ON O.Customer_ID = C.Customer_ID
            JOIN EMPLOYEE E ON O.Employee_ID = E.Employee_ID
            ORDER BY O.Order_Date DESC
        """)
        orders = cursor.fetchall()
    return render(request, 'cafe_app/order_list.html', {'orders': orders})

def customer_menu(request):
    if not request.session.get('customer_id'):
        return redirect('customer_login')

    promotions = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                M.Menu_ID,
                M.Name,
                M.Category,
                M.Price,
                M.Is_Available,
                M.Image,
                dbo.fn_CheckStock(M.Menu_ID) AS Can_Make
            FROM MENU_ITEM M
            WHERE M.Is_Available = 1
        """)
        rows = cursor.fetchall()

        cursor.execute("""
            SELECT Name, Description, Discount_Type, Discount_Value
            FROM PROMOTION
            WHERE Is_Active = 1
            AND Start_Date <= CAST(GETDATE() AS DATE)
            AND End_Date >= CAST(GETDATE() AS DATE)
        """)
        promotions = cursor.fetchall()

    menus = []
    for row in rows:
        menus.append({
            'menu_id': row[0],
            'name': row[1],
            'category': row[2],
            'price': row[3],
            'is_available': row[4],
            'image': row[5],
            'can_make': row[6],
        })

    return render(request, 'cafe_app/customer_menu.html', {
        'menus': menus,
        'promotions': promotions,
        'customer_name': request.session.get('customer_name'),
        'customer_points': request.session.get('customer_points', 0),
    })

def customer_order(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect('customer_login')

        items = request.POST.getlist('menu_id')
        quantities = request.POST.getlist('quantity')
        sweetnesses = request.POST.getlist('sweetness')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO [ORDER] (Customer_ID, Employee_ID, Status, Total_Price)
                OUTPUT INSERTED.Order_ID
                VALUES (%s, 1, 'pending', 0)
            """, [customer_id])
            order_id = int(cursor.fetchone()[0])

            total = 0
            for i, (menu_id, qty) in enumerate(zip(items, quantities)):
                qty = int(qty)
                if qty <= 0:
                    continue
                sweetness = int(sweetnesses[i]) if i < len(sweetnesses) else 100

                cursor.execute("SELECT Price FROM MENU_ITEM WHERE Menu_ID = %s", [menu_id])
                price = float(cursor.fetchone()[0])
                subtotal = price * qty
                total += subtotal

                cursor.execute("""
                    INSERT INTO ORDER_ITEM (Order_ID, Menu_ID, Quantity, Subtotal, Sweetness)
                    VALUES (%s, %s, %s, %s, %s)
                """, [order_id, menu_id, qty, subtotal, sweetness])

            cursor.execute("""
                SELECT ISNULL(MAX(Queue_Number), 0) + 1 FROM QUEUE
                WHERE CAST(Created_At AS DATE) = CAST(GETDATE() AS DATE)
            """)
            queue_number = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO QUEUE (Order_ID, Queue_Number, Status)
                VALUES (%s, %s, 'waiting')
            """, [order_id, queue_number])

        return redirect('customer_queue', order_id=order_id)

    return redirect('customer_menu')

def customer_queue(request, order_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Q.Queue_Number, Q.Status, O.Total_Price,
                   C.First_Name
            FROM QUEUE Q
            JOIN [ORDER] O ON Q.Order_ID = O.Order_ID
            JOIN CUSTOMER C ON O.Customer_ID = C.Customer_ID
            WHERE Q.Order_ID = %s
        """, [order_id])
        queue = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*) FROM QUEUE
            WHERE Status = 'waiting'
            AND Queue_Number < (
                SELECT Queue_Number FROM QUEUE WHERE Order_ID = %s
            )
            AND CAST(Created_At AS DATE) = CAST(GETDATE() AS DATE)
        """, [order_id])
        ahead = cursor.fetchone()[0]

    return render(request, 'cafe_app/customer_queue.html', {
        'queue': queue,
        'ahead': ahead,
        'order_id': order_id,
    })

@login_required
def queue_manage(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                Q.Queue_ID,
                Q.Queue_Number,
                Q.Status,
                C.First_Name,
                O.Total_Price,
                O.Order_ID,
                Q.Created_At
            FROM QUEUE Q
            JOIN [ORDER] O ON Q.Order_ID = O.Order_ID
            JOIN CUSTOMER C ON O.Customer_ID = C.Customer_ID
            WHERE CAST(Q.Created_At AS DATE) = CAST(GETDATE() AS DATE)
            ORDER BY Q.Queue_Number ASC
        """)
        queues_raw = cursor.fetchall()

        queues = []
        for q in queues_raw:
            order_id = q[5]
            cursor.execute("""
                SELECT M.Name, OI.Quantity, OI.Sweetness
                FROM ORDER_ITEM OI
                JOIN MENU_ITEM M ON OI.Menu_ID = M.Menu_ID
                WHERE OI.Order_ID = %s
            """, [order_id])
            items = cursor.fetchall()
            queues.append({
                'queue_id': q[0],
                'queue_number': q[1],
                'status': q[2],
                'customer_name': q[3],
                'total_price': q[4],
                'order_id': q[5],
                'created_at': q[6],
                'items': items
            })                                                                                                                      

    return render(request, 'cafe_app/queue_manage.html', {'queues': queues})

@login_required
def queue_update(request, queue_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE QUEUE SET Status = %s WHERE Queue_ID = %s
            """, [status, queue_id])

            if status == 'done':
                cursor.execute("""
                    UPDATE [ORDER] SET Status = 'done'
                    WHERE Order_ID = (
                        SELECT Order_ID FROM QUEUE WHERE Queue_ID = %s
                    )
                """, [queue_id])

            elif status == 'cancelled':
                cursor.execute("""
                    UPDATE [ORDER] SET Status = 'cancelled'
                    WHERE Order_ID = (
                        SELECT Order_ID FROM QUEUE WHERE Queue_ID = %s
                    )
                """, [queue_id])
                cursor.execute("""
                    DELETE FROM ORDER_ITEM
                    WHERE Order_ID = (
                        SELECT Order_ID FROM QUEUE WHERE Queue_ID = %s
                    )
                """, [queue_id])

        messages.success(request, 'อัปเดตคิวเรียบร้อยแล้ว')
    return redirect('queue_manage')

@login_required
def queue_clear(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM QUEUE
                WHERE CAST(Created_At AS DATE) = CAST(GETDATE() AS DATE)
            """)
        messages.success(request, 'ล้างคิวเรียบร้อยแล้ว')
    return redirect('queue_manage')

def customer_login(request):
    error = None
    if request.method == 'POST':
        phone = request.POST.get('phone')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Customer_ID, First_Name, Last_Name
                FROM CUSTOMER
                WHERE Phone = %s
            """, [phone])
            row = cursor.fetchone()

            if row:
                request.session['customer_id'] = row[0]
                request.session['customer_name'] = row[1] + ' ' + row[2]

                cursor.execute("""
                    SELECT Points, Total_Spent
                    FROM LOYALTY_POINT
                    WHERE Customer_ID = %s
                """, [row[0]])
                loyalty = cursor.fetchone()
                if loyalty:
                    request.session['customer_points'] = loyalty[0]
                    request.session['customer_spent'] = float(loyalty[1])
                else:
                    request.session['customer_points'] = 0
                    request.session['customer_spent'] = 0.0

                return redirect('customer_menu')
            else:
                error = 'ไม่พบเบอร์นี้ในระบบ กรุณาสมัครสมาชิกก่อน'

    return render(request, 'cafe_app/customer_login.html', {'error': error})

def customer_register(request):
    error = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Customer_ID FROM CUSTOMER WHERE Phone = %s
            """, [phone])
            if cursor.fetchone():
                error = 'เบอร์นี้มีในระบบแล้ว กรุณา Login แทน'
            else:
                cursor.execute("""
                    INSERT INTO CUSTOMER (First_Name, Last_Name, Phone, Email)
                    OUTPUT INSERTED.Customer_ID
                    VALUES (%s, %s, %s, %s)
                """, [first_name, last_name, phone, email or None])
                customer_id = int(cursor.fetchone()[0])

                cursor.execute("""
                    INSERT INTO LOYALTY_POINT (Customer_ID, Points, Total_Spent)
                    VALUES (%s, 0, 0)
                """, [customer_id])

                request.session['customer_id'] = customer_id
                request.session['customer_name'] = first_name + ' ' + last_name
                request.session['customer_points'] = 0
                request.session['customer_spent'] = 0.0

                return redirect('customer_menu')

    return render(request, 'cafe_app/customer_register.html', {'error': error})

def customer_logout(request):
    request.session.flush()
    return redirect('customer_login')