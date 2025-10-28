import React, { useState, useEffect } from 'react';
import {
  getAllWorkspaces,
  createWorkspace,
  deleteWorkspace,
  addDataToWorkspace
} from '../services/api';
import WorkspaceTree from '../components/WorkspaceTree';
import WorkspaceDetail from '../components/WorkspaceDetail';
import './WorkspaceManager.css';

const WorkspaceManager = (): React.JSX.Element => {
  const [workspaces, setWorkspaces] = useState([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      const response = await getAllWorkspaces();
      setWorkspaces(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load workspaces');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkspace = async (name, parentPath = null) => {
    try {
      await createWorkspace(name, parentPath);
      loadWorkspaces();
    } catch (err) {
      setError('Failed to create workspace');
      console.error(err);
    }
  };

  const handleDeleteWorkspace = async (path) => {
    try {
      await deleteWorkspace(path);
      loadWorkspaces();
      if (selectedWorkspace && selectedWorkspace.path === path) {
        setSelectedWorkspace(null);
      }
    } catch (err) {
      setError('Failed to delete workspace');
      console.error(err);
    }
  };

  const handleAddData = async (path, key, value) => {
    try {
      await addDataToWorkspace(path, key, value);
      // Refresh the selected workspace
      if (selectedWorkspace && selectedWorkspace.path === path) {
        const response = await getAllWorkspaces();
        setWorkspaces(response.data);
      }
    } catch (err) {
      setError('Failed to add data');
      console.error(err);
    }
  };

  return (
    <div className="workspace-manager">
      <h2>Workspace Manager</h2>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="manager-content">
        <div className="workspace-tree-panel">
          <div className="panel-header">
            <h3>Workspaces</h3>
            <CreateWorkspaceForm onCreate={handleCreateWorkspace} />
          </div>
          {loading ? (
            <div>Loading...</div>
          ) : (
            <WorkspaceTree
              workspaces={workspaces}
              onSelect={setSelectedWorkspace}
              onDelete={handleDeleteWorkspace}
            />
          )}
        </div>

        <div className="workspace-detail-panel">
          <h3>Workspace Details</h3>
          {selectedWorkspace ? (
            <WorkspaceDetail
              workspace={selectedWorkspace}
              onAddData={handleAddData}
            />
          ) : (
            <p>Select a workspace to view details</p>
          )}
        </div>
      </div>
    </div>
  );
};

const CreateWorkspaceForm = ({ onCreate }) => {
  const [name, setName] = useState('');
  const [showForm, setShowForm] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      onCreate(name.trim());
      setName('');
      setShowForm(false);
    }
  };

  if (!showForm) {
    return (
      <button onClick={() => setShowForm(true)} className="btn btn-primary">
        + New Workspace
      </button>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="create-form">
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Workspace name"
        autoFocus
      />
      <div className="form-actions">
        <button type="submit" className="btn btn-primary">Create</button>
        <button type="button" onClick={() => setShowForm(false)} className="btn">Cancel</button>
      </div>
    </form>
  );
};

export default WorkspaceManager;
