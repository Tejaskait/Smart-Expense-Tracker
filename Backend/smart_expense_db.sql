CREATE DATABASE smart_expense_db;
use smart_expense_db;

CREATE USER 'expense_user'@'localhost' IDENTIFIED BY 'smart1234';
GRANT ALL PRIVILEGES ON smart_expense_db.* TO 'expense_user'@'localhost';
FLUSH PRIVILEGES;

desc expenses_expense;
select * from expenses_expense;



USE smart_expense_db;
SHOW TABLES;
DESC expenses_expenses;
SELECT * FROM expenses_expenses;

delete from expenses_expenses;


INSERT INTO expenses_expenses (title, amount, category, date)
VALUES 
('Groceries', 1200.00, 'Food', CURDATE()),
('Netflix', 499.00, 'Entertainment', CURDATE()),
('Bus Ticket', 50.00, NULL, CURDATE());

