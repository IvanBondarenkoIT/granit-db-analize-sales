"""
Кастомный Treeview с поддержкой многострочных ячеек
"""
import tkinter as tk
from tkinter import ttk
from tkinter import font

class MultiLineTreeview(ttk.Treeview):
    """Treeview с поддержкой многострочных ячеек"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_styles()
        
    def _setup_styles(self):
        """Настройка стилей для многострочного отображения"""
        style = ttk.Style()
        
        # Создаем стиль для многострочных ячеек
        style.configure("MultiLine.Treeview", 
                       rowheight=60,  # Увеличиваем высоту строк
                       font=('Consolas', 9))
        
        # Применяем стиль
        self.configure(style="MultiLine.Treeview")
        
    def insert_multiline(self, parent, index, values, **kwargs):
        """Вставка строки с многострочными значениями"""
        # Вычисляем максимальную высоту строки на основе количества строк в ячейках
        max_lines = 1
        for value in values:
            if isinstance(value, str) and '\n' in value:
                lines = value.count('\n') + 1
                max_lines = max(max_lines, lines)
        
        # Устанавливаем высоту строки
        if max_lines > 1:
            self.configure(rowheight=max_lines * 20)
        
        return self.insert(parent, index, values=values, **kwargs)
    
    def _format_cell_content(self, cups, kg, total):
        """Форматирование содержимого ячейки"""
        return f"Чашки: {cups:.0f} шт\nКг: {kg:.2f} кг\nСумма: {total:.2f}"

