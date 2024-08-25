document.addEventListener('DOMContentLoaded', function() {
    // Carregar categorias existentes
    fetch('/api/categories')
        .then(response => response.json())
        .then(categories => {
            const categorySelect = document.getElementById('category-select');
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categorySelect.appendChild(option);
            });
        });

    // Carregar tarefas e estatísticas ao carregar a página
    loadTasks(currentPage);
    loadStats();

    // Adicionar tarefa
    document.getElementById('add-task').addEventListener('click', function() {
        const taskText = document.getElementById('new-task').value;
        const newCategory = document.getElementById('new-category').value;
        const selectedCategory = document.getElementById('category-select').value;
        const taskPriority = document.getElementById('task-priority').value;
        const taskDate = document.getElementById('task-date').value;

        const category = newCategory || selectedCategory;

        const taskData = {
            text: taskText,
            category: category,
            priority: taskPriority,
            date: taskDate,
            color: '#621fb5' // Cor padrão para itens salvos
        };

        console.log(taskData);  // Adicionado para verificar os dados

        fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskData)
        })
        .then(response => response.json())
        .then(task => {
            loadTasks(currentPage); // Recarregar a lista na página atual após adicionar
            document.getElementById('new-task').value = '';
            document.getElementById('new-category').value = '';
            document.getElementById('task-date').value = '';
            loadStats(); // Atualizar o dashboard após adicionar
        });
    });

    // Restante do código permanece o mesmo...
});
