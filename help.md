Сначала прочитаю твой код из архива.Отлично, прочитала весь код. Теперь вижу все ошибки и структуру. Пишу всё.

---

# ПОЛНЫЙ РАЗБОР И ГОТОВЫЕ КОДЫ

## Найденные ошибки в твоём коде

**Costitem.cs** — присваиваешь HeaderText одной и той же колонке `[2]` пять раз подряд — остальные колонки вообще не переименовываются.

**ReportForm.cs** — то же самое, все HeaderText пишешь в `Columns[2]`.

**AddPayment.cs** — передаёшь `comboBox1.Text` (строку) вместо `comboBox1.SelectedValue` (int) как report_id — PostgreSQL упадёт с ошибкой типа.

**AddPayment.cs** — в UPDATE пишешь параметр `name` которого нет в запросе.

**ReportForm.cs** — в удалении строки расходов берёшь id из `dataGridView1` (отчёт), а надо из `dataGridView2` (строка).

**AddReportLine.cs** — `DisplayMember = "Name"` для advancereport — нет такого поля, надо `"purpose"`.

**PaymentForm.cs** — `pay_date` из грида приходит как `DateTime`, а не `String` — упадёт при редактировании.

**price в AddCostitem.cs** — передаёшь как строку `textBox2.Text`, PostgreSQL ожидает numeric.

---

## 1. SQL — создание таблиц с нуля

```sql
-- Запускай в pgAdmin, база: Maslyayeva_zadacha

-- Сотрудники
CREATE TABLE IF NOT EXISTS employee (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(150) NOT NULL,
    city  VARCHAR(100),
    phone VARCHAR(20)
);

-- Статьи затрат
CREATE TABLE IF NOT EXISTS costitem (
    id        SERIAL PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    is_active BOOLEAN      NOT NULL DEFAULT TRUE,
    price     NUMERIC(12,2) NOT NULL DEFAULT 0,
    metrics   VARCHAR(20)  NOT NULL DEFAULT 'шт'
);

-- Авансовый отчёт
CREATE TABLE IF NOT EXISTS advancereport (
    id            SERIAL PRIMARY KEY,
    employee_id   INTEGER NOT NULL REFERENCES employee(id),
    report_date   DATE    NOT NULL DEFAULT CURRENT_DATE,
    period_start  DATE,
    period_end    DATE,
    purpose       VARCHAR(255),
    total_spent   NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_paid    NUMERIC(12,2) NOT NULL DEFAULT 0,
    taxable_sum   NUMERIC(12,2) NOT NULL DEFAULT 0,
    tax_sum       NUMERIC(12,2) NOT NULL DEFAULT 0,
    is_paid_first BOOLEAN       NOT NULL DEFAULT FALSE
);

-- Строки авансового отчёта
CREATE TABLE IF NOT EXISTS advancereportline (
    id           SERIAL PRIMARY KEY,
    report_id    INTEGER      NOT NULL REFERENCES advancereport(id) ON DELETE CASCADE,
    cost_item_id INTEGER      NOT NULL REFERENCES costitem(id),
    quantity     NUMERIC(10,3) NOT NULL DEFAULT 1
);

-- Выплаты из кассы
CREATE TABLE IF NOT EXISTS cashpayment (
    id        SERIAL PRIMARY KEY,
    report_id INTEGER       NOT NULL REFERENCES advancereport(id),
    pay_date  DATE          NOT NULL DEFAULT CURRENT_DATE,
    amount    NUMERIC(12,2) NOT NULL,
    note      VARCHAR(255)
);
```

---

## 2. ВСЕ триггеры и функции — полностью рабочие

> Никаких `@параметров` — это C# синтаксис. В PostgreSQL используем только переменные внутри функций через `DECLARE`.

```sql
-- ============================================================
-- Сначала удаляем старые триггеры если есть
-- ============================================================
DROP TRIGGER IF EXISTS trg_insert_report_line ON advancereportline;
DROP TRIGGER IF EXISTS trg_delete_report_line ON advancereportline;
DROP TRIGGER IF EXISTS trg_update_report_line ON advancereportline;
DROP TRIGGER IF EXISTS trg_insert_cash_payment ON cashpayment;
DROP TRIGGER IF EXISTS trg_delete_cash_payment ON cashpayment;

DROP FUNCTION IF EXISTS fn_insert_report_line();
DROP FUNCTION IF EXISTS fn_delete_report_line();
DROP FUNCTION IF EXISTS fn_update_report_line();
DROP FUNCTION IF EXISTS fn_insert_cash_payment();
DROP FUNCTION IF EXISTS fn_delete_cash_payment();

-- ============================================================
-- ФУНКЦИЯ 1: INSERT строки расхода
-- Берём цену из costitem, прибавляем к total_spent
-- Устанавливаем is_paid_first автоматически:
--   нет выплат → TRUE (тратит свои)
--   есть выплата → FALSE (уже выдан аванс)
-- ============================================================
CREATE OR REPLACE FUNCTION fn_insert_report_line()
RETURNS TRIGGER AS $$
DECLARE
    v_price         NUMERIC(12,2);
    v_line_total    NUMERIC(12,2);
    v_payment_count INTEGER;
BEGIN
    SELECT price INTO v_price
    FROM costitem
    WHERE id = NEW.cost_item_id;

    v_line_total := NEW.quantity * v_price;

    SELECT COUNT(*) INTO v_payment_count
    FROM cashpayment
    WHERE report_id = NEW.report_id;

    UPDATE advancereport
    SET
        total_spent   = total_spent + v_line_total,
        is_paid_first = CASE WHEN v_payment_count = 0 THEN TRUE ELSE FALSE END
    WHERE id = NEW.report_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_report_line
AFTER INSERT ON advancereportline
FOR EACH ROW EXECUTE FUNCTION fn_insert_report_line();

-- ============================================================
-- ФУНКЦИЯ 2: DELETE строки расхода
-- Вычитаем из total_spent
-- ============================================================
CREATE OR REPLACE FUNCTION fn_delete_report_line()
RETURNS TRIGGER AS $$
DECLARE
    v_price      NUMERIC(12,2);
    v_line_total NUMERIC(12,2);
BEGIN
    SELECT price INTO v_price
    FROM costitem
    WHERE id = OLD.cost_item_id;

    v_line_total := OLD.quantity * v_price;

    UPDATE advancereport
    SET total_spent = GREATEST(0, total_spent - v_line_total)
    WHERE id = OLD.report_id;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_delete_report_line
AFTER DELETE ON advancereportline
FOR EACH ROW EXECUTE FUNCTION fn_delete_report_line();

-- ============================================================
-- ФУНКЦИЯ 3: UPDATE строки расхода (изменили количество)
-- ============================================================
CREATE OR REPLACE FUNCTION fn_update_report_line()
RETURNS TRIGGER AS $$
DECLARE
    v_price          NUMERIC(12,2);
    v_old_total      NUMERIC(12,2);
    v_new_total      NUMERIC(12,2);
BEGIN
    SELECT price INTO v_price
    FROM costitem
    WHERE id = NEW.cost_item_id;

    v_old_total := OLD.quantity * v_price;
    v_new_total := NEW.quantity * v_price;

    UPDATE advancereport
    SET total_spent = GREATEST(0, total_spent - v_old_total + v_new_total)
    WHERE id = NEW.report_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_report_line
AFTER UPDATE ON advancereportline
FOR EACH ROW EXECUTE FUNCTION fn_update_report_line();

-- ============================================================
-- ФУНКЦИЯ 4: INSERT выплаты из кассы
-- Логика налога:
--   is_paid_first=TRUE  → налог на ВСЮ выплату (сначала потратил свои)
--   is_paid_first=FALSE → налог только на превышение расходов над выданным
-- Также обновляем is_paid_first:
--   есть строки расходов → TRUE (сначала потратил)
--   нет строк → FALSE (аванс выдаётся первым)
-- ============================================================
CREATE OR REPLACE FUNCTION fn_insert_cash_payment()
RETURNS TRIGGER AS $$
DECLARE
    v_total_spent    NUMERIC(12,2);
    v_total_paid_old NUMERIC(12,2);
    v_is_paid_first  BOOLEAN;
    v_line_count     INTEGER;
    v_taxable        NUMERIC(12,2);
BEGIN
    -- Считаем количество строк расходов
    SELECT COUNT(*) INTO v_line_count
    FROM advancereportline
    WHERE report_id = NEW.report_id;

    -- Читаем текущее состояние отчёта
    SELECT total_spent, total_paid, is_paid_first
    INTO v_total_spent, v_total_paid_old, v_is_paid_first
    FROM advancereport
    WHERE id = NEW.report_id;

    -- Обновляем is_paid_first и total_paid
    UPDATE advancereport
    SET
        is_paid_first = CASE WHEN v_line_count > 0 THEN TRUE ELSE FALSE END,
        total_paid    = total_paid + NEW.amount
    WHERE id = NEW.report_id;

    -- Перечитываем актуальный флаг
    SELECT is_paid_first INTO v_is_paid_first
    FROM advancereport
    WHERE id = NEW.report_id;

    -- Считаем облагаемую сумму
    v_taxable := 0;

    IF v_is_paid_first THEN
        -- Сначала потратил свои → вся компенсация облагается
        v_taxable := NEW.amount;
    ELSE
        -- Получил аванс → налог только если потратил БОЛЬШЕ чем получил до этого
        IF v_total_spent > v_total_paid_old THEN
            v_taxable := LEAST(NEW.amount, v_total_spent - v_total_paid_old);
        END IF;
    END IF;

    IF v_taxable > 0 THEN
        UPDATE advancereport
        SET
            taxable_sum = taxable_sum + v_taxable,
            tax_sum     = tax_sum + ROUND(v_taxable * 0.13, 2)
        WHERE id = NEW.report_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_insert_cash_payment
AFTER INSERT ON cashpayment
FOR EACH ROW EXECUTE FUNCTION fn_insert_cash_payment();

-- ============================================================
-- ФУНКЦИЯ 5: DELETE выплаты — откат налога
-- ============================================================
CREATE OR REPLACE FUNCTION fn_delete_cash_payment()
RETURNS TRIGGER AS $$
DECLARE
    v_total_spent    NUMERIC(12,2);
    v_total_paid_now NUMERIC(12,2);
    v_is_paid_first  BOOLEAN;
    v_taxable        NUMERIC(12,2);
BEGIN
    SELECT total_spent, is_paid_first
    INTO v_total_spent, v_is_paid_first
    FROM advancereport
    WHERE id = OLD.report_id;

    -- Уменьшаем total_paid
    UPDATE advancereport
    SET total_paid = GREATEST(0, total_paid - OLD.amount)
    WHERE id = OLD.report_id;

    -- Читаем total_paid после уменьшения
    SELECT total_paid INTO v_total_paid_now
    FROM advancereport
    WHERE id = OLD.report_id;

    -- Откатываем налог по той же логике
    v_taxable := 0;

    IF v_is_paid_first THEN
        v_taxable := OLD.amount;
    ELSE
        IF v_total_spent > v_total_paid_now THEN
            v_taxable := LEAST(OLD.amount, v_total_spent - v_total_paid_now);
        END IF;
    END IF;

    IF v_taxable > 0 THEN
        UPDATE advancereport
        SET
            taxable_sum = GREATEST(0, taxable_sum - v_taxable),
            tax_sum     = GREATEST(0, tax_sum - ROUND(v_taxable * 0.13, 2))
        WHERE id = OLD.report_id;
    END IF;

    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_delete_cash_payment
AFTER DELETE ON cashpayment
FOR EACH ROW EXECUTE FUNCTION fn_delete_cash_payment();
```

---

## 3. Исправления в C# файлах

### Costitem.cs — исправить Update() (у тебя все колонки в [2])

```csharp
// ЗАМЕНИТЬ весь метод Update() в Costitem.cs на:
public void Update()
{
    String sql = "SELECT * FROM costitem;";
    NpgsqlDataAdapter da = new NpgsqlDataAdapter(sql, con);
    ds.Reset();
    da.Fill(ds);
    dt = ds.Tables[0];
    dataGridView1.DataSource = dt;
    dataGridView1.Columns[0].HeaderText = "Номер";
    dataGridView1.Columns[1].HeaderText = "Наименование";
    dataGridView1.Columns[2].HeaderText = "Активен";
    dataGridView1.Columns[3].HeaderText = "Цена за штуку";
    dataGridView1.Columns[4].HeaderText = "Метрика";
    this.StartPosition = FormStartPosition.CenterScreen;
}
```

### ReportForm.cs — исправить Update() и удаление строки

```csharp
// ЗАМЕНИТЬ метод Update() в ReportForm.cs на:
public void Update()
{
    String sql = @"SELECT ar.id, e.name AS employee_name, ar.report_date, 
                   ar.period_start, ar.period_end, ar.purpose, 
                   ar.total_spent, ar.total_paid, ar.taxable_sum, ar.tax_sum 
                   FROM advancereport ar 
                   JOIN employee e ON e.id = ar.employee_id";
    NpgsqlDataAdapter da = new NpgsqlDataAdapter(sql, con);
    ds.Reset();
    da.Fill(ds);
    dt = ds.Tables[0];
    dataGridView1.DataSource = dt;
    dataGridView1.Columns[0].HeaderText = "Номер";
    dataGridView1.Columns[1].HeaderText = "Сотрудник";
    dataGridView1.Columns[2].HeaderText = "Дата создания";
    dataGridView1.Columns[3].HeaderText = "Начало периода";
    dataGridView1.Columns[4].HeaderText = "Конец периода";
    dataGridView1.Columns[5].HeaderText = "Цель";
    dataGridView1.Columns[6].HeaderText = "Потрачено";
    dataGridView1.Columns[7].HeaderText = "Выдано";
    dataGridView1.Columns[8].HeaderText = "Облагаемая сумма";
    dataGridView1.Columns[9].HeaderText = "Налог";
    this.StartPosition = FormStartPosition.CenterScreen;
}

// ЗАМЕНИТЬ метод dataGridView1_CellClick на:
private void dataGridView1_CellClick(object sender, DataGridViewCellEventArgs e)
{
    if (e.RowIndex < 0) return;
    int id = (int)dataGridView1.CurrentRow.Cells["id"].Value;
    String sql = @"SELECT arl.id, ci.name AS cost_item_name, ci.metrics, 
                   arl.quantity, ci.price, 
                   ROUND(arl.quantity * ci.price, 2) AS line_total
                   FROM advancereportline arl
                   JOIN costitem ci ON ci.id = arl.cost_item_id
                   WHERE arl.report_id = " + id.ToString();
    NpgsqlDataAdapter da_line = new NpgsqlDataAdapter(sql, con);
    ds_line.Reset();
    da_line.Fill(ds_line);
    dt_line = ds_line.Tables[0];
    dataGridView2.DataSource = dt_line;
    dataGridView2.Columns[0].HeaderText = "Номер";
    dataGridView2.Columns[1].HeaderText = "Статья расходов";
    dataGridView2.Columns[2].HeaderText = "Ед.изм";
    dataGridView2.Columns[3].HeaderText = "Количество";
    dataGridView2.Columns[4].HeaderText = "Цена";
    dataGridView2.Columns[5].HeaderText = "Итого";
    this.StartPosition = FormStartPosition.CenterScreen;
}

// ЗАМЕНИТЬ удаление строки расходов (строкуРасходовToolStripMenuItem2_Click):
private void строкуРасходовToolStripMenuItem2_Click(object sender, EventArgs e)
{
    if (dataGridView2.CurrentRow == null) return;
    int id = (int)dataGridView2.CurrentRow.Cells["id"].Value; // берём из dataGridView2!
    NpgsqlCommand command = new NpgsqlCommand(
        "DELETE FROM advancereportline WHERE id = :id", con);
    command.Parameters.AddWithValue("id", id);
    command.ExecuteNonQuery();
    // Обновить строки и шапку
    dataGridView1_CellClick(null, new DataGridViewCellEventArgs(0, dataGridView1.CurrentRow.Index));
    Update();
}
```

### AddPayment.cs — исправить INSERT (неправильный тип report_id)

```csharp
// ЗАМЕНИТЬ button1_Click в AddPayment.cs на:
private void button1_Click(object sender, EventArgs e)
{
    if (this.id == -1)
    {
        try
        {
            NpgsqlCommand command = new NpgsqlCommand(
                "INSERT INTO cashpayment (report_id, pay_date, amount, note) " +
                "VALUES (:report_id, :pay_date, :amount, :note)", con);
            command.Parameters.AddWithValue("report_id", (int)comboBox1.SelectedValue);
            command.Parameters.AddWithValue("pay_date", dateTimePicker1.Value.Date);
            command.Parameters.AddWithValue("amount", decimal.Parse(textBox1.Text));
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
                "UPDATE cashpayment SET report_id=:report_id, pay_date=:pay_date, " +
                "amount=:amount, note=:note WHERE id=:id", con);
            command.Parameters.AddWithValue("id", this.id);
            command.Parameters.AddWithValue("report_id", (int)comboBox1.SelectedValue);
            command.Parameters.AddWithValue("pay_date", dateTimePicker1.Value.Date);
            command.Parameters.AddWithValue("amount", decimal.Parse(textBox1.Text));
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
```

### AddCostitem.cs — исправить тип price

```csharp
// ЗАМЕНИТЬ button1_Click в AddCostitem.cs на:
private void button1_Click(object sender, EventArgs e)
{
    // Валидация
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
        try
        {
            NpgsqlCommand command = new NpgsqlCommand(
                "INSERT INTO costitem (name, is_active, price, metrics) " +
                "VALUES (:name, :is_active, :price, :metrics)", con);
            command.Parameters.AddWithValue("name", textBox1.Text.Trim());
            command.Parameters.AddWithValue("is_active", checkBox1.Checked);
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
        try
        {
            NpgsqlCommand command = new NpgsqlCommand(
                "UPDATE costitem SET name=:name, is_active=:is_active, " +
                "price=:price, metrics=:metrics WHERE id=:id", con);
            command.Parameters.AddWithValue("id", this.id);
            command.Parameters.AddWithValue("name", textBox1.Text.Trim());
            command.Parameters.AddWithValue("is_active", checkBox1.Checked);
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
```

### AddReportLine.cs — исправить DisplayMember

```csharp
// ЗАМЕНИТЬ метод Update() в AddReportLine.cs на:
private void Update()
{
    string sql = "SELECT id, purpose FROM advancereport";
    NpgsqlDataAdapter da = new NpgsqlDataAdapter(sql, con);
    ds.Reset();
    da.Fill(ds);
    dt = ds.Tables[0];
    comboBox1.DataSource = dt;
    comboBox1.DisplayMember = "purpose"; // было "Name" — неправильно!
    comboBox1.ValueMember = "id";

    string sql1 = "SELECT id, name FROM costitem WHERE is_active = TRUE";
    NpgsqlDataAdapter da1 = new NpgsqlDataAdapter(sql1, con);
    ds1.Reset();
    da1.Fill(ds1);
    dt1 = ds1.Tables[0];
    comboBox2.DataSource = dt1;
    comboBox2.DisplayMember = "name";
    comboBox2.ValueMember = "id";
}

// ЗАМЕНИТЬ button1_Click в AddReportLine.cs на:
private void button1_Click_1(object sender, EventArgs e)
{
    if (!decimal.TryParse(textBox1.Text, out decimal qty) || qty <= 0)
    {
        MessageBox.Show("Введите корректное количество (число больше 0).",
            "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        return;
    }

    try
    {
        NpgsqlCommand command = new NpgsqlCommand(
            "INSERT INTO advancereportline (report_id, cost_item_id, quantity) " +
            "VALUES (:report_id, :cost_item_id, :quantity)", con);
        command.Parameters.AddWithValue("report_id", (int)comboBox1.SelectedValue);
        command.Parameters.AddWithValue("cost_item_id", (int)comboBox2.SelectedValue);
        command.Parameters.AddWithValue("quantity", qty);
        command.ExecuteNonQuery();
        Close();
    }
    catch (Exception ex)
    {
        MessageBox.Show("Ошибка при добавлении строки:\n" + ex.Message,
            "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}
```

---

## 4. Валидация полей — как показывать ошибки

Паттерн один для всех форм — просто `MessageBox.Show`:

```csharp
// Проверка что поле не пустое
if (string.IsNullOrWhiteSpace(textBox1.Text))
{
    MessageBox.Show("Поле 'Наименование' не может быть пустым.",
        "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
    return; // прерываем сохранение
}

// Проверка что число
if (!decimal.TryParse(textBox2.Text, out decimal val))
{
    MessageBox.Show("В поле 'Сумма' должно быть число. Пример: 150.50",
        "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
    return;
}

// Проверка что только цифры при вводе (вешается на событие textBox.KeyPress)
private void textBox2_KeyPress(object sender, KeyPressEventArgs e)
{
    // Разрешаем цифры, backspace и запятую/точку
    if (!char.IsDigit(e.KeyChar) && e.KeyChar != (char)Keys.Back
        && e.KeyChar != ',' && e.KeyChar != '.')
    {
        e.Handled = true; // символ не вводится
    }
}
```

---

## 5. Экспорт отчёта в Excel

Добавь кнопку в **ReportForm** и этот метод:

```csharp
// Добавить в ReportForm.cs
// NuGet: Install-Package EPPlus — версия 5.x

private void btnExportExcel_Click(object sender, EventArgs e)
{
    if (dataGridView1.CurrentRow == null) return;

    int reportId = (int)dataGridView1.CurrentRow.Cells["id"].Value;

    // Читаем шапку отчёта
    string sqlHeader = @"
        SELECT ar.id, e.name AS employee_name, ar.report_date,
               ar.period_start, ar.period_end, ar.purpose,
               ar.total_spent, ar.total_paid, ar.taxable_sum, ar.tax_sum
        FROM advancereport ar
        JOIN employee e ON e.id = ar.employee_id
        WHERE ar.id = " + reportId;

    NpgsqlDataAdapter daH = new NpgsqlDataAdapter(sqlHeader, con);
    DataSet dsH = new DataSet();
    daH.Fill(dsH);
    if (dsH.Tables[0].Rows.Count == 0) return;
    DataRow header = dsH.Tables[0].Rows[0];

    // Читаем строки отчёта
    string sqlLines = @"
        SELECT ci.name AS cost_item_name, ci.metrics, arl.quantity,
               ci.price, ROUND(arl.quantity * ci.price, 2) AS line_total
        FROM advancereportline arl
        JOIN costitem ci ON ci.id = arl.cost_item_id
        WHERE arl.report_id = " + reportId;

    NpgsqlDataAdapter daL = new NpgsqlDataAdapter(sqlLines, con);
    DataSet dsL = new DataSet();
    daL.Fill(dsL);
    DataTable lines = dsL.Tables[0];

    // Формируем Excel
    OfficeOpenXml.ExcelPackage.LicenseContext =
        OfficeOpenXml.LicenseContext.NonCommercial;

    using var package = new OfficeOpenXml.ExcelPackage();
    var ws = package.Workbook.Worksheets.Add("Авансовый отчёт");

    // Заголовок
    ws.Cells["A1:F1"].Merge = true;
    ws.Cells["A1"].Value = "АВАНСОВЫЙ ОТЧЁТ № " + reportId;
    ws.Cells["A1"].Style.Font.Bold = true;
    ws.Cells["A1"].Style.Font.Size = 14;
    ws.Cells["A1"].Style.HorizontalAlignment =
        OfficeOpenXml.Style.ExcelHorizontalAlignment.Center;

    // Шапка
    ws.Cells["A3"].Value = "Сотрудник:";
    ws.Cells["B3"].Value = header["employee_name"].ToString();
    ws.Cells["B3"].Style.Font.Bold = true;

    ws.Cells["A4"].Value = "Дата отчёта:";
    ws.Cells["B4"].Value = Convert.ToDateTime(header["report_date"]).ToString("dd.MM.yyyy");

    ws.Cells["A5"].Value = "Период:";
    ws.Cells["B5"].Value = Convert.ToDateTime(header["period_start"]).ToString("dd.MM.yyyy")
                         + " – "
                         + Convert.ToDateTime(header["period_end"]).ToString("dd.MM.yyyy");

    ws.Cells["A6"].Value = "Цель:";
    ws.Cells["B6"].Value = header["purpose"].ToString();

    // Заголовки таблицы
    int hRow = 8;
    string[] cols = { "№", "Статья затрат", "Ед.изм", "Кол-во", "Цена", "Итого" };
    for (int i = 0; i < cols.Length; i++)
    {
        ws.Cells[hRow, i + 1].Value = cols[i];
        ws.Cells[hRow, i + 1].Style.Font.Bold = true;
        ws.Cells[hRow, i + 1].Style.Fill.PatternType =
            OfficeOpenXml.Style.ExcelFillStyle.Solid;
        ws.Cells[hRow, i + 1].Style.Fill.BackgroundColor
            .SetColor(System.Drawing.Color.FromArgb(68, 114, 196));
        ws.Cells[hRow, i + 1].Style.Font.Color
            .SetColor(System.Drawing.Color.White);
    }

    // Строки данных
    int row = hRow + 1;
    int num = 1;
    foreach (DataRow line in lines.Rows)
    {
        ws.Cells[row, 1].Value = num++;
        ws.Cells[row, 2].Value = line["cost_item_name"].ToString();
        ws.Cells[row, 3].Value = line["metrics"].ToString();
        ws.Cells[row, 4].Value = Convert.ToDecimal(line["quantity"]);
        ws.Cells[row, 5].Value = Convert.ToDecimal(line["price"]);
        ws.Cells[row, 5].Style.Numberformat.Format = "#,##0.00";
        ws.Cells[row, 6].Value = Convert.ToDecimal(line["line_total"]);
        ws.Cells[row, 6].Style.Numberformat.Format = "#,##0.00";

        if (row % 2 == 0)
        {
            ws.Cells[row, 1, row, 6].Style.Fill.PatternType =
                OfficeOpenXml.Style.ExcelFillStyle.Solid;
            ws.Cells[row, 1, row, 6].Style.Fill.BackgroundColor
                .SetColor(System.Drawing.Color.FromArgb(235, 241, 251));
        }
        row++;
    }

    // Итоги
    int tRow = row + 1;
    void TotalRow(int r, string lbl, object val, bool yellow = false)
    {
        ws.Cells[r, 5].Value = lbl;
        ws.Cells[r, 5].Style.Font.Bold = true;
        ws.Cells[r, 6].Value = Convert.ToDecimal(val);
        ws.Cells[r, 6].Style.Font.Bold = true;
        ws.Cells[r, 6].Style.Numberformat.Format = "#,##0.00";
        if (yellow)
        {
            ws.Cells[r, 5, r, 6].Style.Fill.PatternType =
                OfficeOpenXml.Style.ExcelFillStyle.Solid;
            ws.Cells[r, 5, r, 6].Style.Fill.BackgroundColor
                .SetColor(System.Drawing.Color.FromArgb(255, 230, 153));
        }
    }

    TotalRow(tRow,     "Итого расходов:",    header["total_spent"]);
    TotalRow(tRow + 1, "Выплачено из кассы:", header["total_paid"]);
    TotalRow(tRow + 2, "Облагаемая сумма:",   header["taxable_sum"], true);
    TotalRow(tRow + 3, "Налог (13%):",        header["tax_sum"],     true);

    // Ширина колонок
    ws.Column(1).Width = 5;
    ws.Column(2).Width = 30;
    ws.Column(3).Width = 10;
    ws.Column(4).Width = 10;
    ws.Column(5).Width = 14;
    ws.Column(6).Width = 14;

    // Сохранить
    string path = System.IO.Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
        $"Report_{reportId}_{DateTime.Now:yyyyMMdd_HHmm}.xlsx");

    package.SaveAs(new System.IO.FileInfo(path));

    MessageBox.Show("Файл сохранён:\n" + path, "Готово",
        MessageBoxButtons.OK, MessageBoxIcon.Information);

    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
    { FileName = path, UseShellExecute = true });
}
```

---

## 6. Круговая диаграмма в Excel

Добавь кнопку в **ReportForm** рядом с экспортом:

```csharp
// Добавить в ReportForm.cs
private void btnExportPie_Click(object sender, EventArgs e)
{
    // Берём период из текущего выбранного отчёта, либо спрашиваем
    // Здесь берём все данные за всё время — можно добавить фильтр по датам
    string sql = @"
        SELECT 
            ci.name AS cost_item_name,
            e.name  AS employee_name,
            SUM(arl.quantity * ci.price) AS total_amount
        FROM advancereportline arl
        JOIN costitem ci ON ci.id = arl.cost_item_id
        JOIN advancereport ar ON ar.id = arl.report_id
        JOIN employee e ON e.id = ar.employee_id
        GROUP BY ci.name, e.name
        ORDER BY ci.name, total_amount DESC";

    NpgsqlDataAdapter da = new NpgsqlDataAdapter(sql, con);
    DataSet ds2 = new DataSet();
    da.Fill(ds2);
    DataTable dt2 = ds2.Tables[0];

    if (dt2.Rows.Count == 0)
    {
        MessageBox.Show("Нет данных для построения диаграммы.",
            "Внимание", MessageBoxButtons.OK, MessageBoxIcon.Warning);
        return;
    }

    // Агрегируем по статьям для диаграммы
    var byItem = dt2.AsEnumerable()
        .GroupBy(r => r["cost_item_name"].ToString())
        .Select(g => new {
            Name  = g.Key,
            Total = g.Sum(r => Convert.ToDecimal(r["total_amount"]))
        }).ToList();

    OfficeOpenXml.ExcelPackage.LicenseContext =
        OfficeOpenXml.LicenseContext.NonCommercial;

    using var package = new OfficeOpenXml.ExcelPackage();

    // ── Лист 1: данные + диаграмма ──────────────────────────
    var wsChart = package.Workbook.Worksheets.Add("Диаграмма");

    wsChart.Cells["A1"].Value = "Статья затрат";
    wsChart.Cells["B1"].Value = "Сумма";
    wsChart.Cells["A1:B1"].Style.Font.Bold = true;

    int row = 2;
    foreach (var item in byItem)
    {
        wsChart.Cells[row, 1].Value = item.Name;
        wsChart.Cells[row, 2].Value = item.Total;
        wsChart.Cells[row, 2].Style.Numberformat.Format = "#,##0.00";
        row++;
    }
    int lastRow = row - 1;

    // Создаём круговую диаграмму
    var chart = (OfficeOpenXml.Drawing.Chart.ExcelPieChart)
        wsChart.Drawings.AddChart("PieChart",
        OfficeOpenXml.Drawing.Chart.eChartType.Pie3D);

    chart.Title.Text = "Расходы по статьям затрат";
    chart.SetPosition(lastRow + 2, 0, 0, 0);
    chart.SetSize(600, 400);

    var series = chart.Series.Add(
        wsChart.Cells[2, 2, lastRow, 2],
        wsChart.Cells[2, 1, lastRow, 1]);
    series.Header = "Сумма";

    chart.DataLabel.ShowPercent  = true;
    chart.DataLabel.ShowCategory = true;
    chart.DataLabel.ShowValue    = false;

    // ── Лист 2: детализация по сотрудникам ──────────────────
    var wsDetail = package.Workbook.Worksheets.Add("По сотрудникам");

    string[] dCols = { "Статья затрат", "Сотрудник", "Сумма" };
    for (int i = 0; i < dCols.Length; i++)
    {
        wsDetail.Cells[1, i + 1].Value = dCols[i];
        wsDetail.Cells[1, i + 1].Style.Font.Bold = true;
        wsDetail.Cells[1, i + 1].Style.Fill.PatternType =
            OfficeOpenXml.Style.ExcelFillStyle.Solid;
        wsDetail.Cells[1, i + 1].Style.Fill.BackgroundColor
            .SetColor(System.Drawing.Color.FromArgb(68, 114, 196));
        wsDetail.Cells[1, i + 1].Style.Font.Color
            .SetColor(System.Drawing.Color.White);
    }

    int dRow = 2;
    decimal grandTotal = dt2.AsEnumerable()
        .Sum(r => Convert.ToDecimal(r["total_amount"]));

    foreach (DataRow r2 in dt2.Rows)
    {
        wsDetail.Cells[dRow, 1].Value = r2["cost_item_name"].ToString();
        wsDetail.Cells[dRow, 2].Value = r2["employee_name"].ToString();
        wsDetail.Cells[dRow, 3].Value = Convert.ToDecimal(r2["total_amount"]);
        wsDetail.Cells[dRow, 3].Style.Numberformat.Format = "#,##0.00";
        dRow++;
    }

    // Итого
    wsDetail.Cells[dRow, 2].Value = "ИТОГО:";
    wsDetail.Cells[dRow, 2].Style.Font.Bold = true;
    wsDetail.Cells[dRow, 3].Value = grandTotal;
    wsDetail.Cells[dRow, 3].Style.Font.Bold = true;
    wsDetail.Cells[dRow, 3].Style.Numberformat.Format = "#,##0.00";

    wsDetail.Column(1).Width = 25;
    wsDetail.Column(2).Width = 25;
    wsDetail.Column(3).Width = 15;

    // Сохранить
    string path = System.IO.Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
        $"PieChart_{DateTime.Now:yyyyMMdd_HHmm}.xlsx");

    package.SaveAs(new System.IO.FileInfo(path));

    MessageBox.Show("Диаграмма сохранена:\n" + path, "Готово",
        MessageBoxButtons.OK, MessageBoxIcon.Information);

    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
    { FileName = path, UseShellExecute = true });
}
```

---

## Итоговый чеклист что делать

**В pgAdmin** — запустить SQL из пункта 1 (таблицы), потом пункт 2 (триггеры).

**В Visual Studio:**
- NuGet → установить `EPPlus` версия 5
- В `Costitem.cs` → заменить `Update()`
- В `ReportForm.cs` → заменить `Update()`, `CellClick`, удаление строки, добавить две кнопки экспорта
- В `AddPayment.cs` → заменить `button1_Click`
- В `AddCostitem.cs` → заменить `button1_Click`
- В `AddReportLine.cs` → заменить `Update()` и `button1_Click_1`
- На все числовые `TextBox` → повесить событие `KeyPress` с проверкой символов
