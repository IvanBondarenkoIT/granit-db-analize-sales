"""
Модуль для анализа продаж кофе
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional
from .database_connector import DatabaseConnector


class CoffeeAnalysis:
    """Класс для анализа продаж кофе"""
    
    def __init__(self, db_connector: DatabaseConnector):
        """
        Инициализация анализатора
        
        Args:
            db_connector: Подключение к базе данных
        """
        self.db = db_connector
        self.sales_data = None
        self.coffee_products = None
        self.stores_info = None
        
        # Настройка стилей для графиков
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def load_data(self, 
                  store_ids: Optional[List[int]] = None,
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None):
        """
        Загрузка данных из базы
        
        Args:
            store_ids: Список ID магазинов
            start_date: Начальная дата
            end_date: Конечная дата
        """
        print("Загрузка данных...")
        
        # Загружаем данные о продажах
        self.sales_data = self.db.get_sales_data(store_ids, start_date, end_date)
        print(f"УСПЕХ: Загружено {len(self.sales_data)} записей о продажах")
        
        # Загружаем информацию о товарах с кофе
        self.coffee_products = self.db.get_coffee_products()
        print(f"УСПЕХ: Загружено {len(self.coffee_products)} товаров с кофе")
        
        # Загружаем информацию о магазинах
        self.stores_info = self.db.get_stores_info()
        print(f"УСПЕХ: Загружено {len(self.stores_info)} магазинов")
        
        # Фильтруем продажи только по товарам с кофе
        coffee_ids = self.coffee_products['ID'].tolist()
        self.sales_data = self.sales_data[self.sales_data['GODSID'].isin(coffee_ids)]
        print(f"УСПЕХ: Отфильтровано {len(self.sales_data)} продаж кофе")
        
        # Преобразуем даты
        self.sales_data['ORDER_DATE'] = pd.to_datetime(self.sales_data['ORDER_DATE'])
        self.sales_data['YEAR'] = self.sales_data['ORDER_DATE'].dt.year
        self.sales_data['MONTH'] = self.sales_data['ORDER_DATE'].dt.month
        self.sales_data['QUARTER'] = self.sales_data['ORDER_DATE'].dt.quarter
        
    def get_sales_summary(self) -> Dict[str, Any]:
        """
        Получение общей сводки по продажам
        
        Returns:
            Dict: Сводка по продажам
        """
        if self.sales_data is None:
            raise Exception("Данные не загружены. Вызовите load_data() сначала.")
        
        summary = {
            'total_sales': self.sales_data['TOTAL_SUM'].sum(),
            'total_quantity': self.sales_data['QUANTITY'].sum(),
            'total_orders': len(self.sales_data),
            'unique_products': self.sales_data['GODSID'].nunique(),
            'unique_stores': self.sales_data['STORE_ID'].nunique(),
            'date_range': {
                'start': self.sales_data['ORDER_DATE'].min(),
                'end': self.sales_data['ORDER_DATE'].max()
            },
            'avg_order_value': self.sales_data['TOTAL_SUM'].mean(),
            'avg_price': self.sales_data['PRICE'].mean()
        }
        
        return summary
    
    def get_sales_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики продаж (алиас для get_sales_summary)
        
        Returns:
            Dict: Статистика продаж
        """
        return self.get_sales_summary()
    
    def sales_by_store(self) -> pd.DataFrame:
        """
        Анализ продаж по магазинам
        
        Returns:
            pd.DataFrame: Продажи по магазинам
        """
        if self.sales_data is None:
            raise Exception("Данные не загружены.")
        
        store_sales = self.sales_data.groupby(['STORE_ID', 'STORE_NAME']).agg({
            'TOTAL_SUM': 'sum',
            'QUANTITY': 'sum',
            'GODSID': 'nunique',
            'ORDER_DATE': 'count'
        }).round(2)
        
        store_sales.columns = ['Общая_сумма', 'Общее_количество', 'Уникальных_товаров', 'Количество_продаж']
        store_sales = store_sales.sort_values('Общая_сумма', ascending=False)
        
        return store_sales
    
    def sales_by_product(self, top_n: int = 20) -> pd.DataFrame:
        """
        Анализ продаж по товарам
        
        Args:
            top_n: Количество топ товаров
            
        Returns:
            pd.DataFrame: Продажи по товарам
        """
        if self.sales_data is None:
            raise Exception("Данные не загружены.")
        
        product_sales = self.sales_data.groupby(['GODSID', 'GOOD_NAME', 'GROUP_NAME']).agg({
            'TOTAL_SUM': 'sum',
            'QUANTITY': 'sum',
            'ORDER_DATE': 'count'
        }).round(2)
        
        product_sales.columns = ['Общая_сумма', 'Общее_количество', 'Количество_продаж']
        product_sales = product_sales.sort_values('Общая_сумма', ascending=False).head(top_n)
        
        return product_sales
    
    def sales_by_time_period(self, period: str = 'month') -> pd.DataFrame:
        """
        Анализ продаж по временным периодам
        
        Args:
            period: Период группировки ('month', 'quarter', 'year')
            
        Returns:
            pd.DataFrame: Продажи по периодам
        """
        if self.sales_data is None:
            raise Exception("Данные не загружены.")
        
        if period == 'month':
            group_col = 'MONTH'
            period_name = 'Месяц'
        elif period == 'quarter':
            group_col = 'QUARTER'
            period_name = 'Квартал'
        elif period == 'year':
            group_col = 'YEAR'
            period_name = 'Год'
        else:
            raise ValueError("Период должен быть 'month', 'quarter' или 'year'")
        
        time_sales = self.sales_data.groupby(group_col).agg({
            'TOTAL_SUM': 'sum',
            'QUANTITY': 'sum',
            'ORDER_DATE': 'count'
        }).round(2)
        
        time_sales.columns = ['Общая_сумма', 'Общее_количество', 'Количество_продаж']
        time_sales.index.name = period_name
        
        return time_sales
    
    def create_sales_charts(self, output_dir: str = 'output'):
        """
        Создание графиков продаж
        
        Args:
            output_dir: Директория для сохранения графиков
        """
        if self.sales_data is None:
            raise Exception("Данные не загружены.")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Продажи по магазинам
        store_sales = self.sales_by_store()
        
        plt.figure(figsize=(12, 8))
        store_sales['Общая_сумма'].plot(kind='bar')
        plt.title('Продажи по магазинам', fontsize=16, fontweight='bold')
        plt.xlabel('Магазин')
        plt.ylabel('Общая сумма продаж')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/sales_by_store.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Топ товары
        product_sales = self.sales_by_product(15)
        
        plt.figure(figsize=(14, 8))
        product_sales['Общая_сумма'].plot(kind='barh')
        plt.title('Топ-15 товаров по продажам', fontsize=16, fontweight='bold')
        plt.xlabel('Общая сумма продаж')
        plt.ylabel('Товар')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/top_products.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Продажи по месяцам
        monthly_sales = self.sales_by_time_period('month')
        
        plt.figure(figsize=(12, 6))
        monthly_sales['Общая_сумма'].plot(kind='line', marker='o')
        plt.title('Продажи по месяцам', fontsize=16, fontweight='bold')
        plt.xlabel('Месяц')
        plt.ylabel('Общая сумма продаж')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/sales_by_month.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Графики сохранены в директории {output_dir}")
    
    def create_interactive_dashboard(self, output_dir: str = 'output'):
        """
        Создание интерактивного дашборда
        
        Args:
            output_dir: Директория для сохранения дашборда
        """
        if self.sales_data is None:
            raise Exception("Данные не загружены.")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Создаем подграфики
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Продажи по магазинам', 'Топ товары', 
                          'Продажи по месяцам', 'Распределение по группам товаров'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # 1. Продажи по магазинам
        store_sales = self.sales_by_store()
        fig.add_trace(
            go.Bar(x=store_sales.index.get_level_values('STORE_NAME'), 
                   y=store_sales['Общая_сумма'],
                   name='Продажи по магазинам'),
            row=1, col=1
        )
        
        # 2. Топ товары
        product_sales = self.sales_by_product(10)
        fig.add_trace(
            go.Bar(x=product_sales['Общая_сумма'],
                   y=product_sales.index.get_level_values('GOOD_NAME'),
                   orientation='h',
                   name='Топ товары'),
            row=1, col=2
        )
        
        # 3. Продажи по месяцам
        monthly_sales = self.sales_by_time_period('month')
        fig.add_trace(
            go.Scatter(x=monthly_sales.index,
                      y=monthly_sales['Общая_сумма'],
                      mode='lines+markers',
                      name='Продажи по месяцам'),
            row=2, col=1
        )
        
        # 4. Распределение по группам товаров
        group_sales = self.sales_data.groupby('GROUP_NAME')['TOTAL_SUM'].sum()
        fig.add_trace(
            go.Pie(labels=group_sales.index,
                   values=group_sales.values,
                   name='Группы товаров'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Дашборд продаж кофе",
            showlegend=False,
            height=800
        )
        
        # Сохраняем как HTML
        fig.write_html(f'{output_dir}/coffee_dashboard.html')
        print(f"Интерактивный дашборд сохранен: {output_dir}/coffee_dashboard.html")
    
    def export_to_excel(self, output_dir: str = 'output'):
        """
        Экспорт данных в Excel
        
        Args:
            output_dir: Директория для сохранения файлов
        """
        if self.sales_data is None:
            raise Exception("Данные не загружены.")
        
        os.makedirs(output_dir, exist_ok=True)
        
        with pd.ExcelWriter(f'{output_dir}/coffee_analysis.xlsx', engine='openpyxl') as writer:
            # Общая сводка
            summary = self.get_sales_summary()
            summary_df = pd.DataFrame(list(summary.items()), columns=['Показатель', 'Значение'])
            summary_df.to_excel(writer, sheet_name='Сводка', index=False)
            
            # Продажи по магазинам
            store_sales = self.sales_by_store()
            store_sales.to_excel(writer, sheet_name='Продажи_по_магазинам')
            
            # Топ товары
            product_sales = self.sales_by_product(50)
            product_sales.to_excel(writer, sheet_name='Топ_товары')
            
            # Продажи по месяцам
            monthly_sales = self.sales_by_time_period('month')
            monthly_sales.to_excel(writer, sheet_name='Продажи_по_месяцам')
            
            # Продажи по кварталам
            quarterly_sales = self.sales_by_time_period('quarter')
            quarterly_sales.to_excel(writer, sheet_name='Продажи_по_кварталам')
            
            # Исходные данные (первые 10000 записей)
            self.sales_data.head(10000).to_excel(writer, sheet_name='Исходные_данные', index=False)
        
        print(f"Данные экспортированы в Excel: {output_dir}/coffee_analysis.xlsx")


if __name__ == "__main__":
    # Пример использования
    with DatabaseConnector() as db:
        if db.test_connection():
            # Создаем анализатор
            analyzer = CoffeeAnalysis(db)
            
            # Загружаем данные за последний год
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
            analyzer.load_data(start_date=start_date, end_date=end_date)
            
            # Выводим сводку
            summary = analyzer.get_sales_summary()
            print("\n📊 СВОДКА ПО ПРОДАЖАМ:")
            for key, value in summary.items():
                print(f"{key}: {value}")
            
            # Создаем отчеты
            analyzer.create_sales_charts()
            analyzer.create_interactive_dashboard()
            analyzer.export_to_excel()
            
            print("\n🎉 Анализ завершен!")
