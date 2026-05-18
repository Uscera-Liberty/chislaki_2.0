## ReportForm.cs — заменить Update() полностью

```csharp
public void Update()
{
    String sql = @"
        SELECT
            ar.id,
            e.name          AS employee_name,
            e.phone         AS employee_phone,
            ar.report_date,
            ar.period_start,
            ar.period_end,
            ar.purpose,
            ar.total_spent,
            COALESCE((
                SELECT SUM(cp.amount)
                FROM cashpayment cp
                WHERE cp.employee_id = ar.employee_id
            ), 0) AS total_paid,
            GREATEST(0,
                ar.total_spent
                -
                COALESCE((
                    SELECT SUM(cp.amount)
                    FROM cashpayment cp
                    WHERE cp.employee_id = ar.employee_id
                      AND cp.pay_date <= ar.report_date
                ), 0)
            ) AS taxable_sum,
            ROUND(
                GREATEST(0,
                    ar.total_spent
                    -
                    COALESCE((
                        SELECT SUM(cp.amount)
                        FROM cashpayment cp
                        WHERE cp.employee_id = ar.employee_id
                          AND cp.pay_date <= ar.report_date
                    ), 0)
                ) * 0.13
            , 2) AS tax_sum
        FROM advancereport ar
        JOIN employee e ON e.id = ar.employee_id
        ORDER BY ar.report_date DESC";

    NpgsqlDataAdapter da = new NpgsqlDataAdapter(sql, con);
    ds.Reset();
    da.Fill(ds);
    dt = ds.Tables[0];
    dataGridView1.DataSource = dt;
    dataGridView1.Columns[0].HeaderText  = "Номер";
    dataGridView1.Columns[1].HeaderText  = "Сотрудник";
    dataGridView1.Columns[2].HeaderText  = "Телефон";
    dataGridView1.Columns[3].HeaderText  = "Дата создания";
    dataGridView1.Columns[4].HeaderText  = "Начало периода";
    dataGridView1.Columns[5].HeaderText  = "Конец периода";
    dataGridView1.Columns[6].HeaderText  = "Цель";
    dataGridView1.Columns[7].HeaderText  = "Потрачено";
    dataGridView1.Columns[8].HeaderText  = "Выдано";
    dataGridView1.Columns[9].HeaderText  = "Облагаемая сумма";
    dataGridView1.Columns[10].HeaderText = "Налог (13%)";
    this.StartPosition = FormStartPosition.CenterScreen;
}
```

---

## ReportForm.cs — заменить dataGridView1_CellClick

Индексы колонок сдвинулись на 1 из-за добавления телефона:

```csharp
private void dataGridView1_CellClick(object sender, DataGridViewCellEventArgs e)
{
    if (e.RowIndex < 0) return;
    int id = (int)dataGridView1.CurrentRow.Cells["id"].Value;
    String sql = @"
        SELECT arl.id, ci.name AS cost_item_name, ci.metrics,
               arl.quantity, ci.price,
               ROUND(arl.quantity * ci.price, 2) AS line_total
        FROM advancereportline arl
        JOIN costitem ci ON ci.id = arl.cost_item_id
        WHERE arl.report_id = " + id.ToString();

    id_report = id;
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
```

---

## EmpoyeeForm.cs — заменить удалитьToolStripMenuItem_Click

Добавляем проверку — если у сотрудника есть отчёты или выплаты, спрашиваем подтверждение:

```csharp
private void удалитьToolStripMenuItem_Click(object sender, EventArgs e)
{
    if (dataGridView1.CurrentRow == null) return;

    int id = (int)dataGridView1.CurrentRow.Cells["ID"].Value;
    string name = dataGridView1.CurrentRow.Cells["name"].Value.ToString();

    // Проверяем есть ли связанные отчёты
    int reportCount = 0;
    int paymentCount = 0;
    try
    {
        NpgsqlCommand cmdCheck = new NpgsqlCommand(
            "SELECT COUNT(*) FROM advancereport WHERE employee_id = :id", con);
        cmdCheck.Parameters.AddWithValue("id", id);
        reportCount = Convert.ToInt32(cmdCheck.ExecuteScalar());

        NpgsqlCommand cmdCheck2 = new NpgsqlCommand(
            "SELECT COUNT(*) FROM cashpayment WHERE employee_id = :id", con);
        cmdCheck2.Parameters.AddWithValue("id", id);
        paymentCount = Convert.ToInt32(cmdCheck2.ExecuteScalar());
    }
    catch (Exception ex)
    {
        MessageBox.Show("Ошибка проверки:\n" + ex.Message,
            "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
        return;
    }

    // Формируем предупреждение
    string warning = $"Вы уверены что хотите удалить сотрудника «{name}»?";
    if (reportCount > 0 || paymentCount > 0)
    {
        warning += $"\n\nВНИМАНИЕ! У сотрудника есть:";
        if (reportCount > 0)
            warning += $"\n• отчётов: {reportCount} шт.";
        if (paymentCount > 0)
            warning += $"\n• выплат: {paymentCount} шт.";
        warning += "\n\nВсе связанные данные будут удалены!";
    }

    DialogResult result = MessageBox.Show(warning, "Подтверждение удаления",
        MessageBoxButtons.YesNo, MessageBoxIcon.Warning);

    if (result != DialogResult.Yes) return;

    try
    {
        NpgsqlCommand command = new NpgsqlCommand(
            "DELETE FROM employee WHERE id = :id", con);
        command.Parameters.AddWithValue("id", id);
        command.ExecuteNonQuery();
        Update();
    }
    catch (Exception ex)
    {
        MessageBox.Show("Ошибка удаления:\n" + ex.Message,
            "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}
```

---

## SQL в pgAdmin — добавить CASCADE на таблицы

Чтобы при удалении сотрудника автоматически удалялись его отчёты и выплаты:

```sql
-- Пересоздаём внешние ключи с CASCADE
ALTER TABLE advancereport
    DROP CONSTRAINT IF EXISTS advancereport_employee_id_fkey,
    ADD CONSTRAINT advancereport_employee_id_fkey
        FOREIGN KEY (employee_id)
        REFERENCES employee(id)
        ON DELETE CASCADE;

ALTER TABLE cashpayment
    DROP CONSTRAINT IF EXISTS cashpayment_employee_id_fkey,
    ADD CONSTRAINT cashpayment_employee_id_fkey
        FOREIGN KEY (employee_id)
        REFERENCES employee(id)
        ON DELETE CASCADE;
```

---

## Итог — что менять

| Файл | Что |
|---|---|
| **ReportForm.cs** | Заменить `Update()` и `dataGridView1_CellClick` |
| **EmpoyeeForm.cs** | Заменить `удалитьToolStripMenuItem_Click` |
| **pgAdmin** | Запустить ALTER TABLE для CASCADE |