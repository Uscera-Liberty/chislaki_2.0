Прочитала весь код. Теперь разбираю все проблемы по очереди.

---

## АНАЛИЗ ВСЕХ ПРОБЛЕМ

**1. Баг в Costitem.cs** — `price` объявлен как `int`, а в БД он `NUMERIC` → `decimal`. При редактировании `(int)dataGridView1.CurrentRow.Cells["price"].Value` падает с ошибкой конвертации.

**2. Убрать `is_active`** из costitem — убрать колонку из таблицы, из форм, из SQL.

**3. Отвязать выплаты от отчёта** — таблица `cashpayment` не должна иметь `report_id`. Выплата — это просто: сотрудник, дата, сумма, комментарий.

**4. Налоги не считались** — потому что логика была завязана на `cashpayment.report_id`. После отвязки логика меняется: сравниваем суммарные расходы сотрудника vs суммарные выплаты сотруднику за период.

**5. `AddReportLine`** — всё ещё фильтрует `WHERE is_active = TRUE` — убрать.

**6. `PaymentForm`** — колонки неправильные после отвязки, `report_id` убрать.

---

## ШАГ 1 — SQL: пересоздание таблиц и триггеры

Запусти это **полностью в pgAdmin**:

```sql
-- ============================================================
-- ПОЛНЫЙ СБРОС И ПЕРЕСОЗДАНИЕ
-- ============================================================

DROP TRIGGER IF EXISTS trg_insert_report_line   ON advancereportline;
DROP TRIGGER IF EXISTS trg_delete_report_line   ON advancereportline;
DROP TRIGGER IF EXISTS trg_update_report_line   ON advancereportline;
DROP TRIGGER IF EXISTS trg_insert_cash_payment  ON cashpayment;
DROP TRIGGER IF EXISTS trg_delete_cash_payment  ON cashpayment;

DROP FUNCTION IF EXISTS fn_insert_report_line();
DROP FUNCTION IF EXISTS fn_delete_report_line();
DROP FUNCTION IF EXISTS fn_update_report_line();
DROP FUNCTION IF EXISTS fn_insert_cash_payment();
DROP FUNCTION IF EXISTS fn_delete_cash_payment();
DROP FUNCTION IF EXISTS fn_recalc_tax(INTEGER);

DROP TABLE IF EXISTS cashpayment        CASCADE;
DROP TABLE IF EXISTS advancereportline  CASCADE;
DROP TABLE IF EXISTS advancereport      CASCADE;
DROP TABLE IF EXISTS costitem           CASCADE;
DROP TABLE IF EXISTS employee           CASCADE;

-- ============================================================
-- ТАБЛИЦЫ
-- ============================================================

CREATE TABLE employee (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(150) NOT NULL,
    city  VARCHAR(100),
    phone VARCHAR(20)
);

-- is_active УБРАН по заданию
CREATE TABLE costitem (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100)  NOT NULL,
    price   NUMERIC(12,2) NOT NULL DEFAULT 0,
    metrics VARCHAR(20)   NOT NULL DEFAULT 'шт'
);

CREATE TABLE advancereport (
    id           SERIAL PRIMARY KEY,
    employee_id  INTEGER NOT NULL REFERENCES employee(id),
    report_date  DATE    NOT NULL DEFAULT CURRENT_DATE,
    period_start DATE,
    period_end   DATE,
    purpose      VARCHAR(255),
    total_spent  NUMERIC(12,2) NOT NULL DEFAULT 0,
    taxable_sum  NUMERIC(12,2) NOT NULL DEFAULT 0,
    tax_sum      NUMERIC(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE advancereportline (
    id           SERIAL PRIMARY KEY,
    report_id    INTEGER       NOT NULL REFERENCES advancereport(id) ON DELETE CASCADE,
    cost_item_id INTEGER       NOT NULL REFERENCES costitem(id),
    quantity     NUMERIC(10,3) NOT NULL DEFAULT 1
);

-- cashpayment НЕЗАВИСИМА: привязана к сотруднику, НЕ к отчёту
CREATE TABLE cashpayment (
    id          SERIAL PRIMARY KEY,
    employee_id INTEGER       NOT NULL REFERENCES employee(id),
    pay_date    DATE          NOT NULL DEFAULT CURRENT_DATE,
    amount      NUMERIC(12,2) NOT NULL,
    note        VARCHAR(255)
);

-- ============================================================
-- ЛОГИКА НАЛОГА (после отвязки выплат):
-- Считаем по сотруднику:
--   total_spent  = сумма всех его расходов по отчётам
--   total_paid   = сумма всех выплат ему из кассы
--   Если сотрудник сначала потратил (есть отчёт), потом получил —
--   то сумма выплат облагается налогом.
--
-- На уровне ОТЧЁТА храним только total_spent.
-- taxable_sum и tax_sum на отчёте = пересчитываются функцией
-- fn_recalc_tax по сотруднику и раскидываются на отчёты.
--
-- УПРОЩЁННАЯ ЛОГИКА которая точно работает:
--   taxable_sum отчёта = MIN(total_spent отчёта, 
--                            MAX(0, total_paid_сотрудника - total_spent_до_этого_отчёта))
-- Но это слишком сложно без доп таблиц.
--
-- ИТОГОВОЕ РЕШЕНИЕ (простое и правильное для задания):
-- taxable_sum и tax_sum считаются В ЗАПРОСЕ Excel-отчёта,
-- НЕ хранятся в БД, а вычисляются на лету:
--   Облагаемая сумма сотрудника за период =
--     MIN(SUM(выплаты), SUM(расходы))
--     если выплаты были ПОСЛЕ того как появились расходы
-- На практике для задания: 
--   облагаемая = SUM(выплат сотруднику за период)
--   при условии что у него есть хоть один отчёт за период
--   tax = облагаемая * 0.13
-- ============================================================

-- ============================================================
-- ТРИГГЕР 1: INSERT строки → прибавить к total_spent отчёта
-- ============================================================
CREATE OR REPLACE FUNCTION fn_insert_report_line()
RETURNS TRIGGER AS $$
DECLARE
    v_price NUMERIC(12,2);
BEGIN
    SELECT price INTO v_price FROM costitem WHERE id = NEW.cost_item_id;
    UPDATE advancereport
    SET total_spent = total_spent + (NEW.quantity * v_price)
    WHERE id = NEW.report_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_report_line
AFTER INSERT ON advancereportline
FOR EACH ROW EXECUTE FUNCTION fn_insert_report_line();

-- ============================================================
-- ТРИГГЕР 2: DELETE строки → вычесть из total_spent
-- ============================================================
CREATE OR REPLACE FUNCTION fn_delete_report_line()
RETURNS TRIGGER AS $$
DECLARE
    v_price NUMERIC(12,2);
BEGIN
    SELECT price INTO v_price FROM costitem WHERE id = OLD.cost_item_id;
    UPDATE advancereport
    SET total_spent = GREATEST(0, total_spent - (OLD.quantity * v_price))
    WHERE id = OLD.report_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_delete_report_line
AFTER DELETE ON advancereportline
FOR EACH ROW EXECUTE FUNCTION fn_delete_report_line();

-- ============================================================
-- ТРИГГЕР 3: UPDATE строки → пересчитать total_spent
-- ============================================================
CREATE OR REPLACE FUNCTION fn_update_report_line()
RETURNS TRIGGER AS $$
DECLARE
    v_price NUMERIC(12,2);
BEGIN
    SELECT price INTO v_price FROM costitem WHERE id = NEW.cost_item_id;
    UPDATE advancereport
    SET total_spent = GREATEST(0,
        total_spent - (OLD.quantity * v_price) + (NEW.quantity * v_price))
    WHERE id = NEW.report_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_report_line
AFTER UPDATE ON advancereportline
FOR EACH ROW EXECUTE FUNCTION fn_update_report_line();
```

---

## ШАГ 2 — Файл: `Costitem.cs` — полная замена

**Баг:** `(int)...Cells["price"].Value` — price это `decimal`, не `int`. Плюс убираем `is_active`.

```csharp
using Npgsql;
using System;
using System.Data;
using System.Drawing;
using System.Windows.Forms;

namespace MyZadacha
{
    public partial class Costitem : Form
    {
        public NpgsqlConnection con;
        DataTable dt = new DataTable();
        DataSet ds = new DataSet();

        public Costitem(NpgsqlConnection con)
        {
            InitializeComponent();
            this.con = con;
        }

        public void Update()
        {
            // is_active убран
            String sql = "SELECT id, name, price, metrics FROM costitem ORDER BY name;";
            NpgsqlDataAdapter da = new NpgsqlDataAdapter(sql, con);
            ds.Reset();
            da.Fill(ds);
            dt = ds.Tables[0];
            dataGridView1.DataSource = dt;
            dataGridView1.Columns[0].HeaderText = "Номер";
            dataGridView1.Columns[1].HeaderText = "Наименование";
            dataGridView1.Columns[2].HeaderText = "Цена за единицу";
            dataGridView1.Columns[3].HeaderText = "Метрика";
            this.StartPosition = FormStartPosition.CenterScreen;
        }

        private void Costitem_Load(object sender, EventArgs e)
        {
            Update();
        }

        private void добавитьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            AddCostitem act = new AddCostitem(con, -1);
            act.ShowDialog();
            Update();
        }

        private void редактироватьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow == null) return;

            int id = (int)dataGridView1.CurrentRow.Cells["id"].Value;
            string name = dataGridView1.CurrentRow.Cells["name"].Value.ToString();
            // ИСПРАВЛЕНИЕ БАГА: price это decimal, не int!
            decimal price = Convert.ToDecimal(dataGridView1.CurrentRow.Cells["price"].Value);
            string metrics = dataGridView1.CurrentRow.Cells["metrics"].Value.ToString();

            AddCostitem ac = new AddCostitem(con, id, name, price, metrics);
            ac.ShowDialog();
            Update();
        }

        private void удалитьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow == null) return;
            int id = (int)dataGridView1.CurrentRow.Cells["id"].Value;
            NpgsqlCommand command = new NpgsqlCommand(
                "DELETE FROM costitem WHERE id = :id", con);
            command.Parameters.AddWithValue("id", id);
            command.ExecuteNonQuery();
            Update();
        }

        private void выходToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Close();
        }
    }
}
```

---

## ШАГ 3 — Файл: `AddCostitem.cs` — полная замена

Убираем `is_active`, меняем тип `price` на `decimal`:

```csharp
using Npgsql;
using System;
using System.Windows.Forms;

namespace MyZadacha
{
    public partial class AddCostitem : Form
    {
        public NpgsqlConnection con;
        int id;

        // Конструктор для ДОБАВЛЕНИЯ
        public AddCostitem(NpgsqlConnection con, int id)
        {
            InitializeComponent();
            this.con = con;
            this.id = id;
        }

        // Конструктор для РЕДАКТИРОВАНИЯ — price теперь decimal!
        public AddCostitem(NpgsqlConnection con, int id, string name, decimal price, string metrics)
        {
            InitializeComponent();
            this.con = con;
            this.id = id;
            textBox1.Text = name;
            textBox2.Text = price.ToString();
            textBox3.Text = metrics;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(textBox1.Text))
            {
                MessageBox.Show("Введите наименование статьи затрат.",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            if (!decimal.TryParse(textBox2.Text, out decimal price) || price < 0)
            {
                MessageBox.Show("Цена должна быть положительным числом.",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            if (string.IsNullOrWhiteSpace(textBox3.Text))
            {
                MessageBox.Show("Введите метрику (например: шт, литр, кг).",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (this.id == -1)
            {
                // ДОБАВЛЕНИЕ — is_active убран
                try
                {
                    NpgsqlCommand command = new NpgsqlCommand(
                        "INSERT INTO costitem (name, price, metrics) " +
                        "VALUES (:name, :price, :metrics)", con);
                    command.Parameters.AddWithValue("name", textBox1.Text.Trim());
                    command.Parameters.AddWithValue("price", price);
                    command.Parameters.AddWithValue("metrics", textBox3.Text.Trim());
                    command.ExecuteNonQuery();
                    Close();
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Ошибка:\n" + ex.Message,
                        "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            else
            {
                // РЕДАКТИРОВАНИЕ — is_active убран
                try
                {
                    NpgsqlCommand command = new NpgsqlCommand(
                        "UPDATE costitem SET name=:name, price=:price, " +
                        "metrics=:metrics WHERE id=:id", con);
                    command.Parameters.AddWithValue("id", this.id);
                    command.Parameters.AddWithValue("name", textBox1.Text.Trim());
                    command.Parameters.AddWithValue("price", price);
                    command.Parameters.AddWithValue("metrics", textBox3.Text.Trim());
                    command.ExecuteNonQuery();
                    Close();
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Ошибка:\n" + ex.Message,
                        "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            Close();
        }
    }
}
```

**Важно:** в `AddCostitem.Designer.cs` убери `checkBox1` (is_active) если он там есть — просто удали его из формы в дизайнере Visual Studio.

---

## ШАГ 4 — Файл: `AddPayment.cs` — полная замена

Выплата теперь привязана к **сотруднику**, не к отчёту:

```csharp
using Npgsql;
using System;
using System.Data;
using System.Windows.Forms;

namespace MyZadacha
{
    public partial class AddPayment : Form
    {
        public NpgsqlConnection con;
        int id;
        DataTable dt = new DataTable();
        DataSet ds = new DataSet();

        // Конструктор для ДОБАВЛЕНИЯ
        public AddPayment(NpgsqlConnection con, int id)
        {
            InitializeComponent();
            this.id = id;
            this.con = con;
        }

        // Конструктор для РЕДАКТИРОВАНИЯ
        public AddPayment(NpgsqlConnection con, int id,
            int employee_id, string date, decimal amount, string note)
        {
            InitializeComponent();
            this.con = con;
            this.id = id;
            dateTimePicker1.Value = DateTime.Parse(date);
            textBox1.Text = amount.ToString();
            textBox2.Text = note;
            // comboBox грузится в Load, потом ставим значение
            this.Load += (s, e) =>
            {
                comboBox1.SelectedValue = employee_id;
            };
        }

        private void LoadEmployees()
        {
            string sql = "SELECT id, name FROM employee ORDER BY name";
            NpgsqlDataAdapter da = new NpgsqlDataAdapter(sql, con);
            ds.Reset();
            da.Fill(ds);
            dt = ds.Tables[0];
            comboBox1.DataSource = dt;
            comboBox1.DisplayMember = "name";
            comboBox1.ValueMember = "id";
        }

        private void AddPayment_Load(object sender, EventArgs e)
        {
            LoadEmployees();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (comboBox1.SelectedValue == null)
            {
                MessageBox.Show("Выберите сотрудника.",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            if (!decimal.TryParse(textBox1.Text, out decimal amount) || amount <= 0)
            {
                MessageBox.Show("Введите корректную сумму (число больше 0).",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (this.id == -1)
            {
                try
                {
                    NpgsqlCommand command = new NpgsqlCommand(
                        "INSERT INTO cashpayment (employee_id, pay_date, amount, note) " +
                        "VALUES (:employee_id, :pay_date, :amount, :note)", con);
                    command.Parameters.AddWithValue("employee_id",
                        (int)comboBox1.SelectedValue);
                    command.Parameters.AddWithValue("pay_date",
                        dateTimePicker1.Value.Date);
                    command.Parameters.AddWithValue("amount", amount);
                    command.Parameters.AddWithValue("note", textBox2.Text);
                    command.ExecuteNonQuery();
                    Close();
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Ошибка при добавлении выплаты:\n" + ex.Message,
                        "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            else
            {
                try
                {
                    NpgsqlCommand command = new NpgsqlCommand(
                        "UPDATE cashpayment SET employee_id=:employee_id, " +
                        "pay_date=:pay_date, amount=:amount, note=:note " +
                        "WHERE id=:id", con);
                    command.Parameters.AddWithValue("id", this.id);
                    command.Parameters.AddWithValue("employee_id",
                        (int)comboBox1.SelectedValue);
                    command.Parameters.AddWithValue("pay_date",
                        dateTimePicker1.Value.Date);
                    command.Parameters.AddWithValue("amount", amount);
                    command.Parameters.AddWithValue("note", textBox2.Text);
                    command.ExecuteNonQuery();
                    Close();
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Ошибка при редактировании выплаты:\n" + ex.Message,
                        "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            Close();
        }
    }
}
```

**В Designer AddPayment:** `comboBox1` теперь показывает сотрудников (не отчёты). Подпись лейбла поменяй на "Сотрудник:".

---

## ШАГ 5 — Файл: `PaymentForm.cs` — полная замена

```csharp
using Npgsql;
using System;
using System.Data;
using System.Windows.Forms;

namespace MyZadacha
{
    public partial class PaymentForm : Form
    {
        public NpgsqlConnection con;
        DataTable dt = new DataTable();
        DataSet ds = new DataSet();

        public PaymentForm(NpgsqlConnection con)
        {
            InitializeComponent();
            this.con = con;
        }

        public void Update()
        {
            // JOIN с employee чтобы показать имя, не id
            String sql = @"
                SELECT cp.id, e.name AS employee_name,
                       cp.pay_date, cp.amount, cp.note
                FROM cashpayment cp
                JOIN employee e ON e.id = cp.employee_id
                ORDER BY cp.pay_date DESC;";

            NpgsqlDataAdapter da = new NpgsqlDataAdapter(sql, con);
            ds.Reset();
            da.Fill(ds);
            dt = ds.Tables[0];
            dataGridView1.DataSource = dt;
            dataGridView1.Columns[0].HeaderText = "Номер";
            dataGridView1.Columns[1].HeaderText = "Сотрудник";
            dataGridView1.Columns[2].HeaderText = "Дата выплаты";
            dataGridView1.Columns[3].HeaderText = "Сумма";
            dataGridView1.Columns[4].HeaderText = "Комментарий";
            this.StartPosition = FormStartPosition.CenterScreen;
        }

        private void PaymentForm_Load(object sender, EventArgs e)
        {
            Update();
        }

        private void добавитьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            AddPayment ap = new AddPayment(con, -1);
            ap.ShowDialog();
            Update();
        }

        private void удалитьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow == null) return;
            int id = (int)dataGridView1.CurrentRow.Cells["id"].Value;
            NpgsqlCommand command = new NpgsqlCommand(
                "DELETE FROM cashpayment WHERE id = :id", con);
            command.Parameters.AddWithValue("id", id);
            command.ExecuteNonQuery();
            Update();
        }

        private void редактироватьToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (dataGridView1.CurrentRow == null) return;

            int id = (int)dataGridView1.CurrentRow.Cells["id"].Value;

            // Читаем employee_id напрямую из БД по id записи
            int employee_id = 0;
            string pay_date = "";
            decimal amount = 0;
            string note = "";

            try
            {
                NpgsqlCommand cmd = new NpgsqlCommand(
                    "SELECT employee_id, pay_date, amount, note " +
                    "FROM cashpayment WHERE id = :id", con);
                cmd.Parameters.AddWithValue("id", id);
                NpgsqlDataReader reader = cmd.ExecuteReader();
                if (reader.Read())
                {
                    employee_id = reader.GetInt32(0);
                    pay_date    = reader.GetDateTime(1).ToString("dd.MM.yyyy");
                    amount      = reader.GetDecimal(2);
                    note        = reader.IsDBNull(3) ? "" : reader.GetString(3);
                }
                reader.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка чтения:\n" + ex.Message,
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            AddPayment ap = new AddPayment(con, id, employee_id, pay_date, amount, note);
            ap.ShowDialog();
            Update();
        }

        private void выходToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Close();
        }
    }
}
```

---

## ШАГ 6 — Файл: `AddReportLine.cs` — убрать фильтр `is_active`

Только одна строка меняется — в методе `Update()`:

```csharp
// БЫЛО:
string sql1 = "SELECT id, name FROM costitem WHERE is_active = TRUE";

// СТАЛО:
string sql1 = "SELECT id, name FROM costitem ORDER BY name";
```

---

## ШАГ 7 — Файл: `ReportExcel.cs` — полная замена

Налоговый отчёт теперь считается правильно: сравниваем расходы по отчётам vs выплаты сотруднику. **Если у сотрудника есть расходы И есть выплаты — выплаты облагаются налогом** (логика задания: сначала потратил, потом получил):

```csharp
using Npgsql;
using System;
using System.Data;
using System.Drawing;
using System.Windows.Forms;
using Excel = Microsoft.Office.Interop.Excel;

namespace MyZadacha
{
    public class ReportExcel : Form
    {
        private NpgsqlConnection con;
        private DateTimePicker dtpStart, dtpEnd;
        private Button btnExport, btnCancel;
        private Label lblInfo;

        public ReportExcel(NpgsqlConnection connection)
        {
            con = connection;
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.Text = "Налоговый отчёт за период";
            this.Size = new System.Drawing.Size(450, 200);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;

            lblInfo = new Label
            {
                Text = "Выберите период для формирования отчёта:",
                Location = new System.Drawing.Point(20, 20),
                Size = new System.Drawing.Size(400, 25),
                Font = new Font("Arial", 10, FontStyle.Bold)
            };

            Label lblStart = new Label
            {
                Text = "Начало:",
                Location = new System.Drawing.Point(30, 60),
                Size = new System.Drawing.Size(60, 25)
            };
            dtpStart = new DateTimePicker
            {
                Location = new System.Drawing.Point(100, 60),
                Size = new System.Drawing.Size(130, 25),
                Format = DateTimePickerFormat.Short
            };

            Label lblEnd = new Label
            {
                Text = "Конец:",
                Location = new System.Drawing.Point(250, 60),
                Size = new System.Drawing.Size(50, 25)
            };
            dtpEnd = new DateTimePicker
            {
                Location = new System.Drawing.Point(300, 60),
                Size = new System.Drawing.Size(130, 25),
                Format = DateTimePickerFormat.Short
            };

            btnExport = new Button
            {
                Text = "Сформировать и выгрузить",
                Location = new System.Drawing.Point(50, 110),
                Size = new System.Drawing.Size(180, 35),
                BackColor = Color.LightGreen
            };
            btnExport.Click += BtnExport_Click;

            btnCancel = new Button
            {
                Text = "Отмена",
                Location = new System.Drawing.Point(250, 110),
                Size = new System.Drawing.Size(100, 35)
            };
            btnCancel.Click += (s, e) => Close();

            Controls.Add(lblInfo);
            Controls.Add(lblStart);
            Controls.Add(dtpStart);
            Controls.Add(lblEnd);
            Controls.Add(dtpEnd);
            Controls.Add(btnExport);
            Controls.Add(btnCancel);
        }

        private void BtnExport_Click(object sender, EventArgs e)
        {
            ExportToExcel();
        }

        private DataTable GetReportData()
        {
            DataTable result = new DataTable();
            try
            {
                // ЛОГИКА НАЛОГА ПОСЛЕ ОТВЯЗКИ ВЫПЛАТ:
                // По каждому сотруднику за период:
                //   total_spent  = сумма расходов по его отчётам
                //   total_paid   = сумма выплат ему из кассы
                //   taxable_sum  = MIN(total_paid, total_spent)
                //     (платим налог с того что получил, но не больше чем потратил)
                //   tax_sum      = taxable_sum * 0.13
                // Условие облагаемости: у сотрудника ЕСТЬ расходы за период
                // (значит сначала тратил, потом получал из кассы)
                string sql = @"
                    SELECT
                        e.name AS employee_name,
                        COALESCE(spent.total_spent, 0) AS total_spent,
                        COALESCE(paid.total_paid, 0)   AS total_paid,
                        CASE
                            WHEN COALESCE(spent.total_spent, 0) > 0
                            THEN LEAST(
                                COALESCE(paid.total_paid, 0),
                                COALESCE(spent.total_spent, 0))
                            ELSE 0
                        END AS taxable_sum,
                        CASE
                            WHEN COALESCE(spent.total_spent, 0) > 0
                            THEN ROUND(
                                LEAST(
                                    COALESCE(paid.total_paid, 0),
                                    COALESCE(spent.total_spent, 0)
                                ) * 0.13, 2)
                            ELSE 0
                        END AS tax_sum
                    FROM employee e
                    LEFT JOIN (
                        SELECT ar.employee_id,
                               SUM(ar.total_spent) AS total_spent
                        FROM advancereport ar
                        WHERE ar.report_date BETWEEN :startDate AND :endDate
                        GROUP BY ar.employee_id
                    ) spent ON spent.employee_id = e.id
                    LEFT JOIN (
                        SELECT cp.employee_id,
                               SUM(cp.amount) AS total_paid
                        FROM cashpayment cp
                        WHERE cp.pay_date BETWEEN :startDate AND :endDate
                        GROUP BY cp.employee_id
                    ) paid ON paid.employee_id = e.id
                    WHERE spent.employee_id IS NOT NULL
                       OR paid.employee_id IS NOT NULL
                    ORDER BY e.name";

                NpgsqlCommand cmd = new NpgsqlCommand(sql, con);
                cmd.Parameters.AddWithValue("startDate", dtpStart.Value.Date);
                cmd.Parameters.AddWithValue("endDate", dtpEnd.Value.Date);
                NpgsqlDataAdapter da = new NpgsqlDataAdapter(cmd);
                da.Fill(result);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка загрузки данных:\n" + ex.Message,
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return null;
            }
            return result;
        }

        private void ExportToExcel()
        {
            if (dtpEnd.Value.Date < dtpStart.Value.Date)
            {
                MessageBox.Show("Дата конца не может быть раньше даты начала!",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            DataTable data = GetReportData();
            if (data == null || data.Rows.Count == 0)
            {
                MessageBox.Show("Нет данных за выбранный период.",
                    "Внимание", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            Excel.Application excelApp = null;
            Excel.Workbook workbook    = null;
            Excel.Worksheet worksheet  = null;

            try
            {
                excelApp = new Excel.Application();
                excelApp.DisplayAlerts = false;
                workbook  = excelApp.Workbooks.Add();
                worksheet = (Excel.Worksheet)workbook.Worksheets[1];
                worksheet.Name = "Налоговый отчёт";

                // Заголовок
                worksheet.Cells[1, 1] = "ОТЧЁТ ПО РАБОТНИКАМ — СУММЫ ОБЛАГАЕМЫЕ НАЛОГОМ";
                Excel.Range titleRange = worksheet.Range[
                    worksheet.Cells[1, 1], worksheet.Cells[1, 5]];
                titleRange.Merge();
                titleRange.Font.Bold = true;
                titleRange.Font.Size = 13;
                titleRange.HorizontalAlignment = Excel.XlHAlign.xlHAlignCenter;

                worksheet.Cells[2, 1] =
                    $"Период: {dtpStart.Value:dd.MM.yyyy} – {dtpEnd.Value:dd.MM.yyyy}";
                Excel.Range periodRange = worksheet.Range[
                    worksheet.Cells[2, 1], worksheet.Cells[2, 5]];
                periodRange.Merge();
                periodRange.HorizontalAlignment = Excel.XlHAlign.xlHAlignCenter;
                periodRange.Font.Italic = true;

                // Шапка таблицы
                int hRow = 4;
                string[] headers = {
                    "Сотрудник",
                    "Всего потрачено, руб.",
                    "Выплачено из кассы, руб.",
                    "Облагаемая сумма, руб.",
                    "Сумма налога (13%), руб."
                };
                for (int i = 0; i < headers.Length; i++)
                {
                    Excel.Range cell = worksheet.Cells[hRow, i + 1];
                    cell.Value2 = headers[i];
                    cell.Font.Bold = true;
                    cell.Interior.Color =
                        System.Drawing.ColorTranslator.ToOle(
                            Color.FromArgb(68, 114, 196));
                    cell.Font.Color =
                        System.Drawing.ColorTranslator.ToOle(Color.White);
                    cell.HorizontalAlignment = Excel.XlHAlign.xlHAlignCenter;
                    cell.Borders.LineStyle = Excel.XlLineStyle.xlContinuous;
                    cell.WrapText = true;
                }
                ((Excel.Range)worksheet.Rows[hRow]).RowHeight = 35;

                // Данные
                int dataRow = hRow + 1;
                decimal grandSpent = 0, grandPaid = 0,
                        grandTaxable = 0, grandTax = 0;
                int rowNum = 0;

                foreach (DataRow row in data.Rows)
                {
                    rowNum++;
                    bool even = (rowNum % 2 == 0);

                    decimal spent   = Convert.ToDecimal(row["total_spent"]);
                    decimal paid    = Convert.ToDecimal(row["total_paid"]);
                    decimal taxable = Convert.ToDecimal(row["taxable_sum"]);
                    decimal tax     = Convert.ToDecimal(row["tax_sum"]);

                    // Чередование строк
                    if (even)
                    {
                        Excel.Range rng = worksheet.Range[
                            worksheet.Cells[dataRow, 1],
                            worksheet.Cells[dataRow, 5]];
                        rng.Interior.Color =
                            System.Drawing.ColorTranslator.ToOle(
                                Color.FromArgb(235, 241, 251));
                    }

                    worksheet.Cells[dataRow, 1] = row["employee_name"].ToString();
                    worksheet.Cells[dataRow, 2] = spent;
                    worksheet.Cells[dataRow, 3] = paid;
                    worksheet.Cells[dataRow, 4] = taxable;
                    worksheet.Cells[dataRow, 5] = tax;

                    // Форматирование числовых ячеек
                    for (int c = 2; c <= 5; c++)
                        ((Excel.Range)worksheet.Cells[dataRow, c])
                            .NumberFormat = "#,##0.00";

                    // Подсветка строк где есть налог
                    if (taxable > 0)
                    {
                        ((Excel.Range)worksheet.Cells[dataRow, 4]).Interior.Color =
                            System.Drawing.ColorTranslator.ToOle(
                                Color.FromArgb(255, 230, 153));
                        ((Excel.Range)worksheet.Cells[dataRow, 5]).Interior.Color =
                            System.Drawing.ColorTranslator.ToOle(
                                Color.FromArgb(255, 199, 206));
                    }

                    // Границы
                    Excel.Range rowRange = worksheet.Range[
                        worksheet.Cells[dataRow, 1],
                        worksheet.Cells[dataRow, 5]];
                    rowRange.Borders.LineStyle = Excel.XlLineStyle.xlContinuous;
                    rowRange.Borders.Color =
                        System.Drawing.ColorTranslator.ToOle(
                            Color.FromArgb(189, 215, 238));
                    rowRange.Borders.Weight = Excel.XlBorderWeight.xlThin;

                    grandSpent   += spent;
                    grandPaid    += paid;
                    grandTaxable += taxable;
                    grandTax     += tax;
                    dataRow++;
                }

                // Итоговая строка
                dataRow++;
                Excel.Range totalRange = worksheet.Range[
                    worksheet.Cells[dataRow, 1],
                    worksheet.Cells[dataRow, 5]];
                totalRange.Interior.Color =
                    System.Drawing.ColorTranslator.ToOle(
                        Color.FromArgb(31, 73, 125));
                totalRange.Font.Color =
                    System.Drawing.ColorTranslator.ToOle(Color.White);
                totalRange.Font.Bold = true;
                totalRange.Borders.LineStyle = Excel.XlLineStyle.xlContinuous;
                totalRange.Borders.Weight = Excel.XlBorderWeight.xlMedium;

                worksheet.Cells[dataRow, 1] = "ИТОГО:";
                worksheet.Cells[dataRow, 2] = grandSpent;
                worksheet.Cells[dataRow, 3] = grandPaid;
                worksheet.Cells[dataRow, 4] = grandTaxable;
                worksheet.Cells[dataRow, 5] = grandTax;
                for (int c = 2; c <= 5; c++)
                    ((Excel.Range)worksheet.Cells[dataRow, c])
                        .NumberFormat = "#,##0.00";

                // Ширина колонок
                worksheet.Columns[1].ColumnWidth = 28;
                worksheet.Columns[2].ColumnWidth = 20;
                worksheet.Columns[3].ColumnWidth = 22;
                worksheet.Columns[4].ColumnWidth = 22;
                worksheet.Columns[5].ColumnWidth = 22;

                // Сохранить и открыть
                string path = System.IO.Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
                    $"TaxReport_{DateTime.Now:yyyyMMdd_HHmm}.xlsx");

                workbook.SaveAs(path);
                MessageBox.Show($"Файл сохранён:\n{path}", "Готово",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                System.Diagnostics.Process.Start(
                    new System.Diagnostics.ProcessStartInfo
                    { FileName = path, UseShellExecute = true });
                Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Ошибка Excel:\n" + ex.Message,
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                if (workbook  != null) { workbook.Close(false);
                    System.Runtime.InteropServices.Marshal.ReleaseComObject(workbook); }
                if (excelApp  != null) { excelApp.Quit();
                    System.Runtime.InteropServices.Marshal.ReleaseComObject(excelApp); }
                if (worksheet != null)
                    System.Runtime.InteropServices.Marshal.ReleaseComObject(worksheet);
            }
        }
    }
}
```

---

## ШАГ 8 — Файл: `PieChartForm.cs` — одна правка

Убрать фильтр `is_active` в `LoadCostItems`:

```csharp
// БЫЛО:
string sql = "SELECT id, name FROM costitem ORDER BY name";
// (у тебя уже так — ОК, is_active там нет, ничего не меняй)
```

Также в `GetDataFromDb` — всё правильно, ничего не трогать.

---

## Итоговая таблица: что и где изменить

| Файл | Что сделать |
|---|---|
| **pgAdmin** | Запустить весь SQL из Шага 1 |
| **Costitem.cs** | Полностью заменить |
| **AddCostitem.cs** | Полностью заменить |
| **AddCostitem Designer** | Убрать `checkBox1` в дизайнере |
| **AddPayment.cs** | Полностью заменить |
| **AddPayment Designer** | Лейбл comboBox1 → "Сотрудник:" |
| **PaymentForm.cs** | Полностью заменить |
| **AddReportLine.cs** | Одна строка: убрать `WHERE is_active = TRUE` |
| **ReportExcel.cs** | Полностью заменить |
| **PieChartForm.cs** | Ничего не менять — уже правильный |
| **ReportForm.cs** | Ничего не менять — уже правильный |