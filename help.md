## EmpoyeeForm.cs — заменить удалитьToolStripMenuItem_Click

```csharp
private void удалитьToolStripMenuItem_Click(object sender, EventArgs e)
{
    if (dataGridView1.CurrentRow == null) return;

    int id = (int)dataGridView1.CurrentRow.Cells["ID"].Value;
    string name = dataGridView1.CurrentRow.Cells["name"].Value.ToString();

    DialogResult result = MessageBox.Show(
        $"Вы уверены что хотите удалить сотрудника «{name}»?",
        "Подтверждение удаления",
        MessageBoxButtons.YesNo,
        MessageBoxIcon.Question);

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