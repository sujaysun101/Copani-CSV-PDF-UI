document.addEventListener('DOMContentLoaded', () => {
    const editButtons = document.querySelectorAll('.edit-btn');
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const saveEditButton = document.getElementById('saveEditBtn');
    const editModal = document.getElementById('editModal');
    const editNameInput = document.getElementById('editName');
    const editValueInput = document.getElementById('editValue');
    const editRowIdInput = document.getElementById('editRowId');
    const csvTable = document.getElementById('csvTable');

    editButtons.forEach(button => {
        button.addEventListener('click', () => {
            const row = button.closest('tr');
            const name = button.dataset.name;
            const value = button.dataset.value;
            const rowId = row.dataset.rowId;

            editNameInput.value = name;
            editValueInput.value = value;
            editRowIdInput.value = rowId;
        });
    });

    saveEditButton.addEventListener('click', () => {
        const rowId = editRowIdInput.value;
        const name = editNameInput.value;
        const value = editValueInput.value;

        fetch(`/edit_csv_row/${rowId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify({ name, value }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const row = document.querySelector(`tr[data-row-id="${rowId}"]`);
                row.cells[0].textContent = name;
                row.cells[1].textContent = value;
                const modal = new bootstrap.Modal(editModal);
                modal.hide();
            } else {
                alert('Error updating CSV data.');
            }
        });
    });

    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            const rowId = button.dataset.rowId;
            if (confirm('Are you sure you want to delete this row?')) {
                fetch(`/delete_csv_row/${rowId}`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        const row = document.querySelector(`tr[data-row-id="${rowId}"]`);
                        row.remove();
                    } else {
                        alert('Error deleting CSV data.');
                    }
                });
            }
        });
    });
});