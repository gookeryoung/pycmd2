export interface WorkspaceModel {
    name: string;
    path: string;
    data: Record<string, string>;
    children: WorkspaceModel[];
    created_at: string;
}
