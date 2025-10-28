import React from 'react';
import WorkspaceManager from './pages/WorkspaceManager';
import './App.css';

export const RootApp = (): React.JSX.Element => {
  return (
    <div className="text-center">
      <header className="bg-main p-12 font-main text-lime-200">
        <h1 className="m-0">MiniDB - Personal Database</h1>
      </header>
      <main>
        <WorkspaceManager />
      </main>
    </div>
  );
}
