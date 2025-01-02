import datetime

class Credits:
    def __init__(self, amount: int):
        self.amount = amount
        self.timestamp = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')  # Automatically generate timestamp

    def to_dict(self):
        return {
            'amount': self.amount,
            'timestamp': self.timestamp
        }
