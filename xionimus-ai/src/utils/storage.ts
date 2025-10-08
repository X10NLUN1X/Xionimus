export const saveTodos = (todos: string[]) => {
  localStorage.setItem('todos', JSON.stringify(todos));
};

export const loadTodos = (): string[] => {
  const data = localStorage.getItem('todos');
  return data ? JSON.parse(data) : [];
};