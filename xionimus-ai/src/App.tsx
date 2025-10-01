import React from 'react';
import { TodoList } from './components/TodoList';

function App() {
  return (
    <div className="app">
      <h1>My Todos</h1>
      <TodoList />
    </div>
  );
}

export default App;