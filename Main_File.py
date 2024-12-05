import numpy as np
from Project_Srinivas import emp_data, sales_data, evaluation_data


class EmployeeAnalytics:
    def __init__(self, emp_data, sales_data, evaluation_data):
        self.emp_data = emp_data
        self.sales_data = sales_data
        self.evaluation_data = evaluation_data

    def get_descriptive_stats(self, metric):
        data = None
        if metric == 'utilization':
            data = self.emp_data['UtilizationRate']
        elif metric == 'sales':
            data = self.sales_data[self.emp_data['JobCode'] == 'D']['Sales']
        elif metric == 'evaluation':
            data = self.emp_data[self.emp_data['JobCode'] == 'C']['EvaluationScore']
        elif metric == 'bonus':
            data = self.emp_data[self.emp_data['Bonus'] > 0]['Bonus']

        if data is None or len(data) == 0:
            return None

        return {
            'count': len(data),
            'min': data.min(),
            'max': data.max(),
            'median': data.median(),
            'mean': data.mean(),
            'std': data.std()
        }

    def get_top_performers(self):
        top_utilization = self.emp_data.loc[self.emp_data['UtilizationRate'].idxmax()]
        directors = self.emp_data[self.emp_data['JobCode'] == 'D']
        top_sales = directors.loc[directors['Sales'].idxmax()] if not directors.empty else None
        return top_utilization, top_sales

    def get_poor_performers(self):
        consultants = self.emp_data[self.emp_data['JobCode'] == 'C']
        util_threshold = consultants['UtilizationRate'].mean() - consultants['UtilizationRate'].std()
        return consultants[
            (consultants['UtilizationRate'] < util_threshold) &
            (consultants['EvaluationScore'] < 1)
            ]


def display_employee(emp):
    print(f"\nID: {emp.name}")
    title = "Consultant" if emp['JobCode'] == 'C' else "Director"
    print(f"{title}: {emp['FirstName']} {emp['LastName']}")
    print(f"Utilization: {emp['UtilizationRate']}")

    if emp['JobCode'] == 'C':
        print(f"Evaluation score: {emp['EvaluationScore']}")
    else:
        print(f"New sales: ${emp['Sales']:,.2f}")

    print(f"Base pay: ${emp['BasePay']:,.2f}")
    print(f"Bonus: ${emp['Bonus']:,.2f}")


analytics = EmployeeAnalytics(emp_data, sales_data, evaluation_data)

while True:
    print("\n1. Search employee")
    print("2. View analytics")
    print("3. View top performers")
    print("4. View poor performers")
    print("5. Exit")

    choice = input("\nEnter choice (1-5): ")

    if choice == '1':
        emp_id = input("Enter employee ID: ")
        if emp_id in emp_data.index:
            display_employee(emp_data.loc[emp_id])
        else:
            print("Employee not found")

    elif choice == '2':
        metrics = ['utilization', 'sales', 'evaluation', 'bonus']
        for metric in metrics:
            stats = analytics.get_descriptive_stats(metric)
            if stats:
                print(f"\n{metric.capitalize()} statistics:")
                for key, value in stats.items():
                    print(f"{key}: {value:,.2f}")

    elif choice == '3':
        top_util, top_sales = analytics.get_top_performers()
        print("\nTop utilization performer:")
        display_employee(top_util)
        if top_sales is not None:
            print("\nTop sales performer:")
            display_employee(top_sales)

    elif choice == '4':
        poor_performers = analytics.get_poor_performers()
        if not poor_performers.empty:
            print("\nPoor performers:")
            for _, emp in poor_performers.iterrows():
                display_employee(emp)
        else:
            print("No poor performers found")

    elif choice == '5':
        break