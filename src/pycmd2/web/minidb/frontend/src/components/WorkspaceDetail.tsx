import React, { useState } from 'react';
import '@/components/WorkspaceDetail.css';

const WorkspaceDetail = ({ workspace, onAddData }): React.JSX.Element => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');

  const handleAddData = (e) => {
    e.preventDefault();
    if (key.trim() && value.trim()) {
      onAddData(workspace.path, key.trim(), value.trim());
      setKey('');
      setValue('');
      setShowAddForm(false);
    }
  };

  // 确保 workspace.data 存在且为对象
  const workspaceData = workspace.data && typeof workspace.data === 'object' ? workspace.data : {};

  return (
    <div className="workspace-detail">
      <div className="workspace-header">
        <h2>{workspace.name}</h2>
        <div className="workspace-path">{workspace.path}</div>
      </div>

      <div className="workspace-info">
        <div className="info-item">
          <strong>Created:</strong> {new Date(workspace.created_at).toLocaleString()}
        </div>
        <div className="info-item">
          <strong>Data Entries:</strong> {Object.keys(workspaceData).length}
        </div>
      </div>

      <div className="data-section">
        <div className="section-header">
          <h3>Data</h3>
          {!showAddForm ? (
            <button
              className="btn btn-primary"
              onClick={() => setShowAddForm(true)}
            >
              + Add Data
            </button>
          ) : (
            <button
              className="btn"
              onClick={() => setShowAddForm(false)}
            >
              Cancel
            </button>
          )}
        </div>

        {showAddForm && (
          <form onSubmit={handleAddData} className="add-data-form">
            <div className="form-group">
              <label>Key:</label>
              <input
                type="text"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="Enter key"
              />
            </div>
            <div className="form-group">
              <label>Value:</label>
              <input
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Enter value"
              />
            </div>
            <button type="submit" className="btn btn-primary">Add</button>
          </form>
        )}

        <div className="data-list">
          {Object.keys(workspaceData).length > 0 ? (
            Object.entries(workspaceData).map(([dataKey, dataValue]) => (
              <div key={dataKey} className="data-item">
                <div className="data-key">{dataKey}</div>
                <div className="data-value">{String(dataValue)}</div>
              </div>
            ))
          ) : (
            <div className="empty-state">No data entries</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkspaceDetail;
