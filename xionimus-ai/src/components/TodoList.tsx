import React, { useState } from 'react';

export const TodoList = () => {
  const [todos, setTodos] = useState<string[]>([]);
  
  return (
    <div>
      {todos.map((todo, i) => <div key={i}>{todo}</div>)}
    </div>
  );
};