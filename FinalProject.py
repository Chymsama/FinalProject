#!/usr/bin/env python
# coding: utf-8

# In[32]:


import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from tkinter.ttk import Treeview
import os

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} - {self.price}VND"

class Order:
    def __init__(self, order_number, items):
        self.order_number = order_number
        self.items = items
        self.is_served = False

    def __str__(self):
        status = "Đã phục vụ" if self.is_served else "Chưa phục vụ"
        items_str = "\n".join([f"{item} x{quantity}" for item, quantity in self.items.items()])
        total_price = sum(item.price * quantity for item, quantity in self.items.items())
        return f"Mã hóa đơn: {self.order_number}\nSản phẩm:\n{items_str}\nTổng tiền: {total_price}VND\nTrạng thái: {status}"

    def save_to_file(self, file):
        file.write(f"Mã hóa đơn: {self.order_number}\n")
        for item, quantity in self.items.items():
            file.write(f"{item} x{quantity}\n")
        file.write(f"Tổng tiền: {self.calculate_total_price()}VND\n")
        file.write(f"Trạng thái: {'Đã phục vụ' if self.is_served else 'Chưa phục vụ'}\n\n")

    def calculate_total_price(self):
        return sum(item.price * quantity for item, quantity in self.items.items())

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý đơn hàng")

        self.menu = [
            MenuItem("Cà phê đen(nóng/đá)", 30000),
            MenuItem("Bạc Xỉu", 28000),
            MenuItem("CaCao", 30000),
            MenuItem("Trà sữa truyền thống", 20000),
            MenuItem("Trà Dâu tươi", 28000),
            MenuItem("Trà Táo Xanh", 28000),
            MenuItem("Soda Việt Quất", 40000),
            MenuItem("Nước Đào Nhài", 25000)
        ]

        self.orders = []

        self.header = tk.Label(root, text="MYAN CAFE")
        self.header.pack()

        self.tree = Treeview(root, columns=("ID", "Số lượng món", "Tổng tiền", "Trạng thái"), show="headings")
        self.tree.heading("ID", text="ID hóa đơn")
        self.tree.heading("Số lượng món", text="Số lượng món")
        self.tree.heading("Tổng tiền", text="Tổng tiền")
        self.tree.heading("Trạng thái", text="Trạng thái")
        self.tree.pack()
        
        
        self.order_button = tk.Button(root, text="Order", command=self.create_order)
        self.order_button.pack()

        edit_order_button = tk.Button(root, text="Sửa đơn hàng", command=self.edit_order)
        edit_order_button.pack()

        serve_order_button = tk.Button(root, text="Đánh dấu đã phục vụ", command=self.serve_order)
        serve_order_button.pack()
        
        
        self.search_order_button = tk.Button(root, text="Tìm hóa đơn", command=self.search_order)
        self.search_order_button.pack()

        self.quit_button = tk.Button(root, text="Thoát", command=root.quit)
        self.quit_button.pack()

    def create_order(self):
        order_window = tk.Toplevel(self.root)
        order_window.title("Tạo hóa đơn")

        self.selected_items = {}
        for item in self.menu:
            item_frame = tk.Frame(order_window)
            item_label = tk.Label(item_frame, text=str(item))
            quantity_entry = tk.Entry(item_frame, width=5)

            item_label.pack(side=tk.LEFT)
            quantity_entry.pack(side=tk.RIGHT)
            item_frame.pack()

            self.selected_items[item] = quantity_entry

        confirm_button = tk.Button(order_window, text="Xác nhận", command=lambda: self.confirm_order(order_window))
        confirm_button.pack()

    
    def confirm_order(self, order_window):
        order_items = {}
        for item, entry in self.selected_items.items():
            quantity = entry.get()
            if quantity and int(quantity) > 0:
                order_items[item] = int(quantity)
        if order_items:
            order_number = len(self.orders) + 1
            order = Order(order_number, order_items)
            self.orders.append(order)
            self.save_order_to_file(order)
            self.tree.insert("", "end", values=(order.order_number, len(order.items), order.calculate_total_price(), "Chưa phục vụ"))
            total_price = order.calculate_total_price()
            messagebox.showinfo("Thông báo", f"Đã tạo hóa đơn và lưu thành công!\nTổng tiền: {total_price}VND")
            order_window.destroy()

    def view_orders(self):
        if not self.orders:
            messagebox.showinfo("Thông báo", "Chưa có đơn hàng nào được tạo.")
            return

        orders_str = "\n\n".join([str(order) for order in self.orders])
        orders_window = tk.Toplevel(self.root)
        orders_window.title("Danh sách đơn hàng")
        orders_label = tk.Label(orders_window, text=orders_str)
        orders_label.pack()

        edit_order_button = tk.Button(orders_window, text="Sửa đơn hàng", command=self.edit_order)
        edit_order_button.pack()

        serve_order_button = tk.Button(orders_window, text="Đánh dấu đã phục vụ", command=self.serve_order)
        serve_order_button.pack()

    def edit_order(self):
        selected_order_str = simpledialog.askstring("Sửa đơn hàng", "Nhập mã hóa đơn bạn muốn sửa:")
        if selected_order_str is not None:
            selected_order_number = int(selected_order_str)
            for order in self.orders:
                if order.order_number == selected_order_number:
                    self.edit_order_details(order)
                    break
            else:
                messagebox.showinfo("Thông báo", f"Không tìm thấy hóa đơn có mã {selected_order_number}.")

    def edit_order_details(self, order):
        order_window = tk.Toplevel(self.root)
        order_window.title("Sửa đơn hàng")

        self.selected_items = {}
        for item in self.menu:
            item_frame = tk.Frame(order_window)
            item_label = tk.Label(item_frame, text=str(item))
            quantity_entry = tk.Entry(item_frame, width=5)
            if item in order.items:
                quantity_entry.insert(0, order.items[item])

            item_label.pack(side=tk.LEFT)
            quantity_entry.pack(side=tk.RIGHT)
            item_frame.pack()

            self.selected_items[item] = quantity_entry

        confirm_button = tk.Button(order_window, text="Xác nhận", command=lambda: self.confirm_edit(order, order_window))
        confirm_button.pack()

    def confirm_edit(self, order, order_window):
        order_items = {}
        for item, entry in self.selected_items.items():
            quantity = entry.get()
            if quantity and int(quantity) > 0:
                order_items[item] = int(quantity)
        order.items = order_items
        messagebox.showinfo("Thông báo", "Đã sửa đơn hàng thành công!")
        order_window.destroy()

    def serve_order(self):
        selected_order_str = simpledialog.askstring("Đánh dấu đã phục vụ", "Nhập mã hóa đơn bạn muốn đánh dấu đã phục vụ:")
        if selected_order_str is not None:
            selected_order_number = int(selected_order_str)
            for order in self.orders:
                if order.order_number == selected_order_number:
                    order.is_served = True
                    messagebox.showinfo("Thông báo", "Đã đánh dấu hóa đơn đã phục vụ!")
                    break
            else:
                messagebox.showinfo("Thông báo", f"Không tìm thấy hóa đơn có mã {selected_order_number}.")

    def save_order_to_file(self, order):
        directory_path = r"C:\Users\ASUS\FinalProject"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        file_path = os.path.join(directory_path, f"order_{order.order_number}.txt")

        with open(file_path, "w", encoding="utf-8") as file:
            order.save_to_file(file)

    def search_order(self):
        order_number = simpledialog.askinteger("Tìm hóa đơn", "Nhập mã hóa đơn:")
        if order_number is not None:
            found_order = None
            for order in self.orders:
                if order.order_number == order_number:
                    found_order = order
                    break

            if found_order:
                messagebox.showinfo("Hóa đơn", str(found_order))
            else:
                messagebox.showinfo("Thông báo", f"Không tìm thấy hóa đơn có mã {order_number}.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

