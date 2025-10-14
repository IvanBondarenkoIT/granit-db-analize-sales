"""
GUI приложение для анализа продаж кофе
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime, timedelta
import os
import traceback
from .database_connector import DatabaseConnector
from .remote_db_connector import RemoteDatabaseConnector
from .logger_config import setup_logger
# from multi_line_treeview import MultiLineTreeview
import re

# Настройка логирования
logger = setup_logger("coffee_gui")


class CoffeeAnalysisGUI:
    """Главное окно приложения"""
    
    def __init__(self, root):
        logger.info("Инициализация GUI приложения")
        self.root = root
        self.root.title("Анализ продаж кофе - Гранит ДБ")
        self.root.geometry("1200x800")
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Переменные
        self.db_connector = None
        self.sales_data = None
        self.stores_data = None
        self.products_data = None
        self.db_type = "local"  # Тип БД: "local" или "remote"
        
        # Создаем интерфейс
        try:
            self.create_widgets()
            logger.info("GUI интерфейс создан успешно")
        except Exception as e:
            logger.error(f"Ошибка создания GUI интерфейса: {e}")
            logger.error(traceback.format_exc())
            raise
        
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 1. Секция подключения к БД
        self.create_connection_section(main_frame, 0)
        
        # 2. Секция параметров отчета
        self.create_parameters_section(main_frame, 1)
        
        # 3. Секция генерации отчета
        self.create_report_section(main_frame, 2)
        
        # 4. Секция стиля отображения
        self.create_display_style_section(main_frame, 3)
        
        # 5. Секция отображения результатов
        self.create_results_section(main_frame, 4)
        
    def create_connection_section(self, parent, row):
        """Создание секции подключения к БД"""
        # Фрейм подключения
        conn_frame = ttk.LabelFrame(parent, text="Подключение к базе данных", padding="10")
        conn_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Выбор типа БД
        db_type_frame = ttk.Frame(conn_frame)
        db_type_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(db_type_frame, text="Тип БД:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.db_type_var = tk.StringVar(value="local")
        ttk.Radiobutton(db_type_frame, text="Локальная БД", 
                        variable=self.db_type_var, value="local",
                        command=self.on_db_type_change).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(db_type_frame, text="Удаленная БД (только чтение)", 
                        variable=self.db_type_var, value="remote",
                        command=self.on_db_type_change).pack(side=tk.LEFT)
        
        # Фрейм для локальной БД
        self.local_frame = ttk.Frame(conn_frame)
        self.local_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Путь к локальной БД
        ttk.Label(self.local_frame, text="Путь к БД:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.db_path_var = tk.StringVar(value="D:\\Granit DB\\GEORGIA.GDB")
        ttk.Entry(self.local_frame, textvariable=self.db_path_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(self.local_frame, text="Обзор", command=self.browse_db_file).grid(row=0, column=2)
        
        # Фрейм для удаленной БД
        self.remote_frame = ttk.Frame(conn_frame)
        self.remote_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))
        self.remote_frame.grid_remove()  # Скрыть по умолчанию
        
        # Сервер
        ttk.Label(self.remote_frame, text="Сервер:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.remote_host_var = tk.StringVar(value="85.114.224.45")
        ttk.Entry(self.remote_frame, textvariable=self.remote_host_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        ttk.Label(self.remote_frame, text="Порт:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.remote_port_var = tk.StringVar(value="3055")
        ttk.Entry(self.remote_frame, textvariable=self.remote_port_var, width=8).grid(row=0, column=3, sticky=tk.W)
        
        # Алиас БД
        ttk.Label(self.remote_frame, text="Алиас БД:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.remote_db_var = tk.StringVar(value="DK_GEORGIA")
        ttk.Entry(self.remote_frame, textvariable=self.remote_db_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        
        ttk.Label(self.remote_frame, text="🔒 READ-ONLY режим", 
                  foreground="green", font=('Arial', 9, 'bold')).grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Общие параметры (пользователь и пароль)
        cred_frame = ttk.Frame(conn_frame)
        cred_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Пользователь
        ttk.Label(cred_frame, text="Пользователь:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.db_user_var = tk.StringVar(value="SYSDBA")
        ttk.Entry(cred_frame, textvariable=self.db_user_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        # Пароль
        ttk.Label(cred_frame, text="Пароль:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.db_password_var = tk.StringVar(value="masterkey")
        ttk.Entry(cred_frame, textvariable=self.db_password_var, show="*", width=20).grid(row=0, column=3, sticky=tk.W)
        
        # Кнопки подключения
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
        
        self.connect_btn = ttk.Button(btn_frame, text="Подключиться", command=self.connect_to_db)
        self.connect_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(btn_frame, text="Отключиться", command=self.disconnect_from_db, state="disabled")
        self.disconnect_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Статус подключения
        self.connection_status_var = tk.StringVar(value="Не подключено")
        self.connection_status_label = ttk.Label(btn_frame, textvariable=self.connection_status_var, foreground="red")
        self.connection_status_label.grid(row=0, column=2, padx=(15, 0))
        
        conn_frame.columnconfigure(1, weight=1)
    
    def on_db_type_change(self):
        """Обработчик переключения типа БД"""
        db_type = self.db_type_var.get()
        
        if db_type == "local":
            self.local_frame.grid()
            self.remote_frame.grid_remove()
            logger.info("Переключено на локальную БД")
        else:
            self.local_frame.grid_remove()
            self.remote_frame.grid()
            logger.info("Переключено на удаленную БД")
        
    def create_parameters_section(self, parent, row):
        """Создание секции параметров отчета"""
        # Фрейм параметров
        params_frame = ttk.LabelFrame(parent, text="Параметры отчета", padding="10")
        params_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Период
        ttk.Label(params_frame, text="Период с:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        ttk.Entry(params_frame, textvariable=self.start_date_var, width=12).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(params_frame, text="по:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(params_frame, textvariable=self.end_date_var, width=12).grid(row=0, column=3, sticky=tk.W)
        
        # Группировка по времени
        ttk.Label(params_frame, text="Группировка:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.time_grouping_var = tk.StringVar(value="day")
        time_grouping_combo = ttk.Combobox(params_frame, textvariable=self.time_grouping_var, 
                                          values=["day", "week", "month"], state="readonly", width=10)
        time_grouping_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Магазины
        ttk.Label(params_frame, text="Магазины:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.stores_frame = ttk.Frame(params_frame)
        self.stores_frame.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Чекбоксы для магазинов будут добавлены после подключения к БД
        
    def create_report_section(self, parent, row):
        """Создание секции генерации отчета"""
        # Фрейм генерации отчета
        report_frame = ttk.LabelFrame(parent, text="Генерация отчета", padding="10")
        report_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Кнопка генерации отчета
        self.generate_btn = ttk.Button(report_frame, text="Сгенерировать отчет", 
                                      command=self.generate_report, state="disabled")
        self.generate_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Кнопка экспорта
        self.export_btn = ttk.Button(report_frame, text="Экспорт в Excel", 
                                    command=self.export_to_excel, state="disabled")
        self.export_btn.grid(row=0, column=1)
        
    def create_display_style_section(self, parent, row):
        """Создание секции стиля отображения"""
        # Фрейм стиля отображения
        style_frame = ttk.LabelFrame(parent, text="Стиль отображения", padding="10")
        style_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Выбор стиля отображения
        ttk.Label(style_frame, text="Стиль таблицы:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.display_style_var = tk.StringVar(value="detailed")
        style_combo = ttk.Combobox(style_frame, textvariable=self.display_style_var, 
                                  values=["detailed", "compact"], state="readonly", width=15)
        style_combo.grid(row=0, column=1, sticky=tk.W)
        
        # Описания стилей
        ttk.Label(style_frame, text="Подробный - многострочные ячейки с детальной информацией", 
                 font=('Arial', 8)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        ttk.Label(style_frame, text="Компактный - одна строка с эмодзи и сокращенными данными", 
                 font=('Arial', 8)).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        
    def create_results_section(self, parent, row):
        """Создание секции отображения результатов"""
        # Фрейм результатов
        results_frame = ttk.LabelFrame(parent, text="Результаты", padding="10")
        results_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        
        # Создаем Treeview для отображения таблицы
        self.tree_frame = ttk.Frame(results_frame)
        self.tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(self.tree_frame, 
                                yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Размещение элементов
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Настройка растягивания
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(row, weight=1)
        
    def browse_db_file(self):
        """Выбор файла базы данных"""
        filename = filedialog.askopenfilename(
            title="Выберите файл базы данных",
            filetypes=[("Firebird Database", "*.gdb *.fdb"), ("All files", "*.*")]
        )
        if filename:
            self.db_path_var.set(filename)
            
    def connect_to_db(self):
        """Подключение к базе данных (локальной или удаленной)"""
        db_type = self.db_type_var.get()
        logger.info(f"Попытка подключения к {db_type} базе данных")
        
        try:
            user = self.db_user_var.get()
            password = self.db_password_var.get()
            
            if db_type == "local":
                # Подключение к локальной БД
                db_path = self.db_path_var.get()
                logger.info(f"Локальная БД: путь={db_path}, пользователь={user}")
                
                self.db_connector = DatabaseConnector(
                    db_path=db_path,
                    user=user,
                    password=password
                )
                
                if self.db_connector.connect():
                    logger.info("Подключение к локальной БД установлено")
                    if self.db_connector.test_connection():
                        self._on_connection_success("Локальная БД")
                    else:
                        self._on_connection_failed("Тест подключения не прошел")
                else:
                    self._on_connection_failed("Не удалось подключиться")
                    
            else:
                # Подключение к удаленной БД
                host = self.remote_host_var.get()
                port = int(self.remote_port_var.get())
                database = self.remote_db_var.get()
                
                logger.info(f"Удаленная БД: {host}:{port}/{database}, пользователь={user}")
                
                self.db_connector = RemoteDatabaseConnector(
                    host=host,
                    port=port,
                    database_path=database,
                    user=user,
                    password=password
                )
                
                # Тест подключения к удаленной БД
                success, message = self.db_connector.test_connection()
                if success:
                    logger.info("Подключение к удаленной БД установлено")
                    self._on_connection_success("Удаленная БД (READ-ONLY)")
                else:
                    self._on_connection_failed(f"Ошибка: {message}")
                
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            logger.error(traceback.format_exc())
            self._on_connection_failed(str(e))
    
    def _on_connection_success(self, db_type_name):
        """Обработчик успешного подключения"""
        logger.info(f"Подключение к {db_type_name} успешно")
        self.connection_status_var.set(f"Подключено ({db_type_name})")
        self.connection_status_label.config(foreground="green")
        self.generate_btn.config(state="normal")
        self.connect_btn.config(state="disabled")
        self.disconnect_btn.config(state="normal")
        self.load_stores()
        messagebox.showinfo("Успех", f"Подключение к {db_type_name} установлено!")
    
    def _on_connection_failed(self, error_message):
        """Обработчик неудачного подключения"""
        logger.error(f"Ошибка подключения: {error_message}")
        self.connection_status_var.set("Ошибка подключения")
        self.connection_status_label.config(foreground="red")
        messagebox.showerror("Ошибка", f"Не удалось подключиться к БД!\n{error_message}")
    
    def disconnect_from_db(self):
        """Безопасное отключение от базы данных"""
        logger.info("Отключение от базы данных")
        try:
            if self.db_connector:
                # Для локальной БД вызываем disconnect(), для удаленной просто удаляем объект
                if isinstance(self.db_connector, DatabaseConnector):
                    self.db_connector.disconnect()
                self.db_connector = None
                
                self.connection_status_var.set("Отключено")
                self.connection_status_label.config(foreground="gray")
                self.generate_btn.config(state="disabled")
                self.export_btn.config(state="disabled")
                self.connect_btn.config(state="normal")
                self.disconnect_btn.config(state="disabled")
                # Очищаем список магазинов
                for widget in self.stores_frame.winfo_children():
                    widget.destroy()
                logger.info("Отключение от БД выполнено успешно")
        except Exception as e:
            logger.error(f"Ошибка при отключении от БД: {e}")
            messagebox.showwarning("Предупреждение", f"Ошибка при отключении: {str(e)}")
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        logger.info("Закрытие приложения")
        try:
            # Безопасно отключаемся от БД
            if self.db_connector:
                self.disconnect_from_db()
            # Закрываем окно
            self.root.destroy()
        except Exception as e:
            logger.error(f"Ошибка при закрытии приложения: {e}")
            # Принудительно закрываем окно
            self.root.destroy()
            
    def load_stores(self):
        """Загрузка списка магазинов"""
        logger.info("Загрузка списка магазинов")
        if not self.db_connector:
            logger.warning("Нет подключения к БД для загрузки магазинов")
            return
            
        try:
            logger.info("Получение информации о магазинах из БД")
            
            # Для удаленной БД используем execute_query_to_dataframe
            if isinstance(self.db_connector, RemoteDatabaseConnector):
                query = "SELECT ID, NAME FROM STORGRP ORDER BY NAME"
                self.stores_data = self.db_connector.execute_query_to_dataframe(query)
            else:
                self.stores_data = self.db_connector.get_stores_info()
                
            logger.info(f"Загружено {len(self.stores_data)} магазинов")
            
            # Очищаем предыдущие чекбоксы
            for widget in self.stores_frame.winfo_children():
                widget.destroy()
                
            # Создаем чекбоксы для магазинов
            self.store_vars = {}
            row = 0
            col = 0
            for i, store in self.stores_data.iterrows():
                var = tk.BooleanVar(value=True)  # По умолчанию все выбраны
                self.store_vars[store['ID']] = var
                
                cb = ttk.Checkbutton(self.stores_frame, text=store['NAME'], variable=var)
                cb.grid(row=row, column=col, sticky=tk.W, padx=(0, 20))
                
                col += 1
                if col > 2:  # 3 колонки
                    col = 0
                    row += 1
                    
            logger.info("Чекбоксы магазинов созданы успешно")
                    
        except Exception as e:
            logger.error(f"Ошибка загрузки магазинов: {e}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Ошибка", f"Ошибка загрузки магазинов: {str(e)}")
            
    def extract_weight_from_name(self, name):
        """Извлекает вес из названия товара"""
        patterns = [
            r'\((\d+(?:\.\d+)?)\s*kg\)',  # (1kg), (0.5kg)
            r'\((\d+(?:\.\d+)?)\s*g\)',   # (250g), (500g)
            r'\((\d+(?:\.\d+)?)\s*г\)',   # (250г)
            r'(\d+(?:\.\d+)?)\s*kg\b',    # 1kg, 0.5kg
            r'(\d+(?:\.\d+)?)\s*g\b',     # 250g, 500g
            r'(\d+(?:\.\d+)?)\s*г\b',     # 250г
            r'(\d+(?:\.\d+)?)\s*,\s*(\d+)\s*g',  # 0,500 g
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Для паттерна с запятой
                    weight = float(match.group(1)) + float(match.group(2)) / 1000
                else:
                    weight = float(match.group(1))
                
                # Конвертируем граммы в килограммы
                if 'g' in pattern or 'г' in pattern:
                    weight = weight / 1000
                return weight
        
        return 0.25  # Значение по умолчанию для кофе (250г)
        
    def generate_report(self):
        """Генерация отчета"""
        logger.info("Начало генерации отчета")
        if not self.db_connector:
            logger.error("Нет подключения к БД для генерации отчета")
            messagebox.showinfo("Ошибка", "Сначала подключитесь к базе данных!")
            return
            
        try:
            # Получаем выбранные магазины
            selected_stores = [store_id for store_id, var in self.store_vars.items() if var.get()]
            logger.info(f"Выбранные магазины: {selected_stores}")
            if not selected_stores:
                logger.warning("Не выбрано ни одного магазина")
                messagebox.showinfo("Ошибка", "Выберите хотя бы один магазин!")
                return
                
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            logger.info(f"Период анализа: {start_date} - {end_date}")
                
            # Загружаем данные с правильным расчетом килограммов
            logger.info("Загрузка данных о продажах кофе с пачками")
            
            if isinstance(self.db_connector, RemoteDatabaseConnector):
                # Для удаленной БД выполняем запрос напрямую
                self.sales_data = self._get_remote_sales_data(selected_stores, start_date, end_date)
            else:
                # Для локальной БД используем существующий метод
                self.sales_data = self.db_connector.get_coffee_sales_with_packages(
                    store_ids=selected_stores,
                    start_date=start_date,
                    end_date=end_date
                )
            
            logger.info(f"Загружено {len(self.sales_data)} записей о продажах")
            
            if self.sales_data.empty:
                logger.warning("Нет данных за выбранный период")
                messagebox.showinfo("Информация", "Нет данных за выбранный период!")
                return
            
            # Переименовываем колонки для совместимости
            logger.info("Переименование колонок")
            self.sales_data = self.sales_data.rename(columns={
                'ALLCUP': 'QUANTITY',
                'PACKAGES_KG': 'TOTAL_WEIGHT_KG',
                'TOTAL_CASH': 'TOTAL_SUM'
            })
            
            # Преобразуем даты
            self.sales_data['ORDER_DATE'] = pd.to_datetime(self.sales_data['ORDER_DATE'])
            
            # Группируем данные
            logger.info("Создание таблицы отчета")
            self.create_report_table()
            
            self.export_btn.config(state="normal")
            logger.info("Отчет сгенерирован успешно")
            messagebox.showinfo("Успех", "Отчет сгенерирован!")
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            logger.error(traceback.format_exc())
            messagebox.showerror("Ошибка", f"Ошибка генерации отчета: {str(e)}")
    
    def _get_remote_sales_data(self, store_ids, start_date, end_date):
        """Получение данных о продажах из удаленной БД"""
        logger.info("Получение данных из удаленной БД")
        
        # Формируем список ID магазинов для SQL запроса
        store_ids_str = ','.join([str(sid) for sid in store_ids])
        
        # Запрос 1: Данные о чашках и суммах
        cups_query = f"""
        SELECT 
            stgp.name as STORE_NAME,
            D.DAT_ as ORDER_DATE,
            COUNT(*) AS ALLCUP,
            SUM(D.SUMMA) AS TOTAL_CASH
        FROM STORZAKAZDT D 
        JOIN STORGRP stgp ON D.STORGRPID = stgp.ID 
        WHERE D.STORGRPID IN ({store_ids_str})
        AND D.CSDTKTHBID IN ('1', '2', '3') 
        AND D.DAT_ >= '{start_date}' AND D.DAT_ <= '{end_date}'
        GROUP BY stgp.name, D.DAT_
        """
        
        # Запрос 2: Килограммы пачек
        packages_query = f"""
        SELECT 
            stgp.name as STORE_NAME,
            D.DAT_ as ORDER_DATE,
            SUM(GD.SOURCE) as PACKAGES_KG
        FROM STORZAKAZDT D 
        JOIN STORZDTGDS GD ON D.ID = GD.SZID 
        JOIN Goods G ON GD.GodsID = G.ID 
        JOIN STORGRP stgp ON D.STORGRPID = stgp.id 
        WHERE D.STORGRPID IN ({store_ids_str})
        AND D.CSDTKTHBID IN ('1', '2', '3') 
        AND D.DAT_ >= '{start_date}' AND D.DAT_ <= '{end_date}'
        AND (
            (G.NAME LIKE '%250 g%' OR G.NAME LIKE '%250г%' OR
             G.NAME LIKE '%500 g%' OR G.NAME LIKE '%500г%' OR
             G.NAME LIKE '%1 kg%' OR G.NAME LIKE '%1кг%' OR
             G.NAME LIKE '%200 g%' OR G.NAME LIKE '%200г%' OR
             G.NAME LIKE '%125 g%' OR G.NAME LIKE '%125г%')
            AND (G.NAME LIKE '%Coffee%' OR G.NAME LIKE '%кофе%' OR 
                 G.NAME LIKE '%Кофе%' OR G.NAME LIKE '%Blaser%')
        )
        GROUP BY stgp.name, D.DAT_
        """
        
        logger.info("Выполнение запроса чашек и сумм...")
        df_cups = self.db_connector.execute_query_to_dataframe(cups_query)
        
        logger.info("Выполнение запроса килограммов...")
        df_packages = self.db_connector.execute_query_to_dataframe(packages_query)
        
        # Объединяем данные
        df = df_cups.merge(
            df_packages,
            on=['STORE_NAME', 'ORDER_DATE'],
            how='left'
        )
        
        # Заполняем пропущенные килограммы нулями
        df['PACKAGES_KG'] = df['PACKAGES_KG'].fillna(0)
        
        logger.info(f"Получено {len(df)} записей из удаленной БД")
        
        return df
            
    def create_report_table(self):
        """Создание таблицы отчета"""
        logger.info("Создание таблицы отчета")
        # Очищаем предыдущие данные
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Определяем группировку по времени
        time_grouping = self.time_grouping_var.get()
        if time_grouping == "day":
            self.sales_data['TIME_PERIOD'] = self.sales_data['ORDER_DATE'].dt.date
        elif time_grouping == "week":
            self.sales_data['TIME_PERIOD'] = self.sales_data['ORDER_DATE'].dt.to_period('W').dt.start_time.dt.date
        elif time_grouping == "month":
            self.sales_data['TIME_PERIOD'] = self.sales_data['ORDER_DATE'].dt.to_period('M').dt.start_time.dt.date
            
        # Группируем данные
        grouped = self.sales_data.groupby(['STORE_NAME', 'TIME_PERIOD']).agg({
            'QUANTITY': 'sum',  # Чашки (AllCup)
            'TOTAL_WEIGHT_KG': 'sum',  # Килограммы (PACKAGES_KG)
            'TOTAL_SUM': 'sum',  # Общая сумма (TOTAL_CASH)
        }).reset_index()
        
        # Создаем сводную таблицу
        pivot_table = grouped.pivot_table(
            index='STORE_NAME',
            columns='TIME_PERIOD',
            values=['QUANTITY', 'TOTAL_WEIGHT_KG', 'TOTAL_SUM'],
            fill_value=0
        )
        
        # Настраиваем колонки дерева
        time_periods = sorted(grouped['TIME_PERIOD'].unique())
        
        # Создаем колонки: Магазин + периоды
        columns = ['Магазин']
        for period in time_periods:
            columns.append(str(period))
            
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Настраиваем стиль для многострочных ячеек
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=70)  # Увеличиваем высоту строк для трех строчек
        self.tree.configure(style="Custom.Treeview")
        
        # Настраиваем заголовки
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
                    
                # Формируем ячейку в зависимости от стиля
                display_style = self.display_style_var.get()
                if display_style == "detailed":
                    cell_content = f"Чашки: {cups:.0f} шт\nКг: {kg:.2f} кг\nСумма: {total:.2f} лари"
                else:  # compact
                    cell_content = f"☕ {cups:.0f}шт\n📦 {kg:.1f}кг\n💰 {total:.0f} лари"
                values.append(cell_content)
                
            self.tree.insert('', 'end', values=values)
        
        logger.info(f"Таблица создана: {len(pivot_table)} магазинов, {len(time_periods)} периодов")
            
    def export_to_excel(self):
        """Экспорт отчета в Excel"""
        if not hasattr(self, 'sales_data') or self.sales_data is None:
            messagebox.showerror("Ошибка", "Сначала сгенерируйте отчет!")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Сохранить отчет как"
            )
            
            if filename:
                # Создаем сводную таблицу для экспорта
                time_grouping = self.time_grouping_var.get()
                if time_grouping == "day":
                    self.sales_data['TIME_PERIOD'] = self.sales_data['ORDER_DATE'].dt.date
                elif time_grouping == "week":
                    self.sales_data['TIME_PERIOD'] = self.sales_data['ORDER_DATE'].dt.to_period('W').dt.start_time.dt.date
                elif time_grouping == "month":
                    self.sales_data['TIME_PERIOD'] = self.sales_data['ORDER_DATE'].dt.to_period('M').dt.start_time.dt.date
                    
                grouped = self.sales_data.groupby(['STORE_NAME', 'TIME_PERIOD']).agg({
                    'QUANTITY': 'sum',
                    'TOTAL_WEIGHT_KG': 'sum',
                    'TOTAL_SUM': 'sum'
                }).reset_index()
                
                # Экспортируем
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    grouped.to_excel(writer, sheet_name='Детальный отчет', index=False)
                    
                    # Создаем сводную таблицу
                    pivot_table = grouped.pivot_table(
                        index='STORE_NAME',
                        columns='TIME_PERIOD',
                        values=['QUANTITY', 'TOTAL_WEIGHT_KG', 'TOTAL_SUM'],
                        fill_value=0
                    )
                    pivot_table.to_excel(writer, sheet_name='Сводная таблица')
                
                messagebox.showinfo("Успех", f"Отчет сохранен: {filename}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")


def main():
    """Запуск приложения"""
    logger.info("Запуск GUI приложения")
    try:
        root = tk.Tk()
        logger.info("Создано главное окно tkinter")
        app = CoffeeAnalysisGUI(root)
        logger.info("GUI приложение инициализировано")
        root.mainloop()
        logger.info("GUI приложение завершено")
    except Exception as e:
        logger.error(f"Критическая ошибка в main(): {e}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
