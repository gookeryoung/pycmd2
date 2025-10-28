import React, { useState } from 'react';
import './WorkspaceTree.css';
import { WorkspaceModel } from '@/models/WorkspaceModel';

interface WorkspaceTreeProps {
  workspaces: WorkspaceModel[];
  onSelect: (workspace: any) => void;
  onDelete: (path: string) => void;
}


/** WorkspaceTree组件
 * 树形结构组件，用于展示和操作 Workspace 数据
 * @param {WorkspaceModel[]} workspaces - Workspace 数据列表
 * @param {(workspace: any) => void} onSelect - 选中 Workspace 的回调函数
 * @param {(path: string) => void} onDelete - 删除 Workspace 的回调函数
 */
const WorkspaceTree = ({ workspaces, onSelect, onDelete }: WorkspaceTreeProps): React.JSX.Element => {
  const isEmpty = workspaces.length === 0;

  return (
    <div className="text-left">
      {workspaces.map(workspace => (
        <WorkspaceTreeNode
          key={workspace.path}
          workspace={workspace}
          level={0}
          onSelect={onSelect}
          onDelete={onDelete}
        />
      ))}

      {isEmpty && (
        <div className="bg-empty text-red-600">
          当前目录下未发现任何 Workspaces, 请先初始化!
        </div>
      )}
    </div>
  );
};

interface WorkspaceTreeNodeProps {
  workspace: WorkspaceModel;
  level: number;
  onSelect: (workspace: any) => void;
  onDelete: (path: string) => void;
}

const WorkspaceTreeNode = ({ workspace, level, onSelect, onDelete }: WorkspaceTreeNodeProps) => {
  const [expanded, setExpanded] = useState(false);

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  const handleSelect = () => {
    onSelect(workspace);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete "${workspace.name}"?`)) {
      onDelete(workspace.path);
    }
  };

  console.log(`workspace: ${JSON.stringify(workspace)}`)

  return (
    <div className="workspace-node">
      <div
        className={`node-row ${level > 0 ? 'child-node' : ''}`}
        style={{ paddingLeft: `${level * 20}px` }}
        onClick={handleSelect}
      >
        <span className="node-toggle" onClick={(e) => { e.stopPropagation(); handleToggle(); }}>
          {workspace.has_children ? (expanded ? "v" : '>') : '•'}
        </span>
        <span className="node-name">{workspace.name}</span>
        <span className="node-meta">
          {workspace.data_count > 0 && `(${workspace.data_count})`}
        </span>
        <button className="delete-btn" onClick={handleDelete}>×</button>
      </div>

      {expanded && workspace.children && (
        <div className="node-children">
          {workspace.children.map(child => (
            <WorkspaceTreeNode
              key={child.path}
              workspace={child}
              level={level + 1}
              onSelect={onSelect}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default WorkspaceTree;
