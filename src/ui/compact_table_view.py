"""
Компактное отображение таблицы с данными в ячейках
"""
import tkinter as tk
from tkinter import ttk
import pandas as pd

class CompactTableView:
    """Компактное отображение таблицы с группированными данными"""
    
    def __init__(self, parent):
        self.parent = parent
        self.tree = None
        self.setup_tree()
        
    def setup_tree(self):
        """Настройка Treeview для компактного отображения"""
        # Создаем фрейм для таблицы
        self.tree_frame = ttk.Frame(self.parent)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(self.tree_frame, 
                                yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Размещение
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Настройка растягивания
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        
        # Стиль для многострочных ячеек
        style = ttk.Style()
        style.configure("Compact.Treeview", rowheight=70)  # Увеличиваем высоту для трех строчек
        self.tree.configure(style="Compact.Treeview")
        
    def create_table(self, sales_data, time_grouping="day"):
        """Создание таблицы с данными"""
        # Очищаем предыдущие данные
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Определяем группировку по времени
        if time_grouping == "day":
            sales_data['TIME_PERIOD'] = sales_data['ORDER_DATE'].dt.date
        elif time_grouping == "week":
            sales_data['TIME_PERIOD'] = sales_data['ORDER_DATE'].dt.to_period('W').dt.start_time.dt.date
        elif time_grouping == "month":
            sales_data['TIME_PERIOD'] = sales_data['ORDER_DATE'].dt.to_period('M').dt.start_time.dt.date
            
        # Группируем данные
        grouped = sales_data.groupby(['STORE_NAME', 'TIME_PERIOD']).agg({
            'QUANTITY': 'sum',  # Чашки
            'TOTAL_WEIGHT_KG': 'sum',  # Килограммы
            'TOTAL_SUM': 'sum',  # Общая сумма
        }).reset_index()
        
        # Создаем сводную таблицу
        pivot_table = grouped.pivot_table(
            index='STORE_NAME',
            columns='TIME_PERIOD',
            values=['QUANTITY', 'TOTAL_WEIGHT_KG', 'TOTAL_SUM'],
            fill_value=0
        )
        
        # Настраиваем колонки
        time_periods = sorted(grouped['TIME_PERIOD'].unique())
        columns = ['Магазин'] + [str(p) for p in time_periods]
        
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Настраиваем заголовки и ширину колонок
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Магазин':
                self.tree.column(col, width=180, anchor='w')
            else:
                self.tree.column(col, width=160, anchor='center')
        
        # Заполняем данными
        for store in pivot_table.index:
            values = [store]
            for period in time_periods:
                if period in pivot_table.columns.get_level_values(1):
                    cups = pivot_table.loc[store, ('QUANTITY', period)]
                    kg = pivot_table.loc[store, ('TOTAL_WEIGHT_KG', period)]
                    total = pivot_table.loc[store, ('TOTAL_SUM', period)]
                else:
                    cups = kg = total = 0
                    
                # Формируем компактную ячейку
                cell_content = f"☕ {cups:.0f}шт \n 📦 {kg:.1f}кг \n 💰 {total:.0f}"
                values.append(cell_content)
                
            self.tree.insert('', 'end', values=values)
        
        return len(pivot_table), len(time_periods)
