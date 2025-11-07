import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Progress } from "./ui/progress";
import { Project, Task, Tag } from "../App";
import { FolderOpen, CheckCircle, Clock, ExternalLink, Edit2, Search } from "lucide-react";
import { CreateProjectDialog } from "./CreateProjectDialog";
import { EditProjectDialog } from "./EditProjectDialog";

type ProjectsScreenProps = {
  projects: Project[];
  tasks: Task[];
  tags: Tag[];
  navigateTo: (screen: string, itemId?: string) => void;
  selectedProjectId?: string | null;
  onProjectCreate: (project: Project) => void;
  onProjectUpdate: (project: Project) => void;
};

export function ProjectsScreen({
  projects,
  tasks,
  tags,
  navigateTo,
  selectedProjectId,
  onProjectCreate,
  onProjectUpdate,
}: ProjectsScreenProps) {
  const [selectedProject, setSelectedProject] = useState<Project | null>(
    selectedProjectId ? projects.find((p) => p.id === selectedProjectId) || null : null
  );
  const [searchQuery, setSearchQuery] = useState("");

  const filterProjects = (projectsList: Project[]) => {
    if (!searchQuery) return projectsList;
    const query = searchQuery.toLowerCase();
    return projectsList.filter(
      (project) =>
        project.title.toLowerCase().includes(query) ||
        project.description?.toLowerCase().includes(query)
    );
  };

  const getProjectTasks = (project: Project) => {
    return tasks.filter((t) => t.projectId === project.id);
  };

  const getProjectProgress = (project: Project) => {
    const projectTasks = getProjectTasks(project);
    if (projectTasks.length === 0) return 0;
    const completedTasks = projectTasks.filter((t) => t.status === "completed");
    return Math.round((completedTasks.length / projectTasks.length) * 100);
  };

  const activeProjects = filterProjects(projects.filter((p) => p.status === "active"));
  const completedProjects = filterProjects(projects.filter((p) => p.status === "completed"));
  const onHoldProjects = filterProjects(projects.filter((p) => p.status === "on_hold"));
  const cancelledProjects = filterProjects(projects.filter((p) => p.status === "cancelled"));

  const renderProjectCard = (project: Project) => {
    const progress = getProjectProgress(project);
    const projectTasks = getProjectTasks(project);
    const completedCount = projectTasks.filter((t) => t.status === "completed").length;

    return (
      <Card
        key={project.id}
        className={`cursor-pointer transition-all ${
          selectedProject?.id === project.id
            ? "border-blue-500 shadow-md"
            : "hover:border-neutral-300"
        }`}
        onClick={() => setSelectedProject(project)}
      >
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-base">{project.title}</CardTitle>
              <CardDescription className="text-xs mt-1">
                {project.createdAt.toLocaleDateString('ja-JP')} 作成
              </CardDescription>
            </div>
            {project.status === "completed" && (
              <CheckCircle className="size-5 text-green-600" />
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-neutral-600 line-clamp-2">{project.description}</p>
          <div>
            <div className="flex justify-between text-xs text-neutral-500 mb-1">
              <span>進捗</span>
              <span>
                {completedCount} / {projectTasks.length} タスク
              </span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* ヘッ��ー */}
      <div className="p-6 border-b bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1>プロジェクト</h1>
            <p className="text-neutral-600 mt-1">
              複数のタスクをまとめたプロジェクト ({projects.length}件)
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* 検索バー */}
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-neutral-400" />
              <Input
                placeholder="プロジェクトを検索..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <CreateProjectDialog onCreateProject={onProjectCreate} />
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="flex-1 overflow-hidden p-6">
        <div className="h-full grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* プロジェクト一覧 */}
          <div className="space-y-6 lg:col-span-2 overflow-y-auto">
            {/* アクティブ */}
            {activeProjects.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <FolderOpen className="size-5 text-slate-900" />
                  <h2>進行中</h2>
                  <Badge variant="secondary">{activeProjects.length}</Badge>
                </div>
                {activeProjects.map((project) => renderProjectCard(project))}
              </div>
            )}

            {/* 完了 */}
            {completedProjects.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <CheckCircle className="size-5 text-slate-900" />
                  <h2>完了</h2>
                  <Badge variant="secondary">{completedProjects.length}</Badge>
                </div>
                {completedProjects.map((project) => renderProjectCard(project))}
              </div>
            )}

            {/* 保留 */}
            {onHoldProjects.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Clock className="size-5 text-slate-900" />
                  <h2>保留</h2>
                  <Badge variant="secondary">{onHoldProjects.length}</Badge>
                </div>
                {onHoldProjects.map((project) => renderProjectCard(project))}
              </div>
            )}

            {/* キャンセル */}
            {cancelledProjects.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Clock className="size-5 text-slate-900" />
                  <h2>キャンセル</h2>
                  <Badge variant="secondary">{cancelledProjects.length}</Badge>
                </div>
                {cancelledProjects.map((project) => renderProjectCard(project))}
              </div>
            )}

            {projects.length === 0 && (
              <Card>
                <CardContent className="py-8">
                  <p className="text-center text-neutral-500">
                    プロジェクトはありません
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* プロジェクト詳細 */}
          <div className="lg:col-span-3">
            {selectedProject ? (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle>{selectedProject.title}</CardTitle>
                        <CardDescription className="mt-1">
                          {selectedProject.createdAt.toLocaleDateString('ja-JP')} 作成
                        </CardDescription>
                      </div>
                      <Badge
                        variant={
                          selectedProject.status === "active"
                            ? "default"
                            : selectedProject.status === "completed"
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {selectedProject.status === "active" && "進行中"}
                        {selectedProject.status === "completed" && "完了"}
                        {selectedProject.status === "on_hold" && "保留中"}
                        {selectedProject.status === "cancelled" && "キャンセル"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="text-sm text-neutral-500 mb-2">説明</div>
                      <p>{selectedProject.description}</p>
                    </div>
                    <div>
                      <div className="text-sm text-neutral-500 mb-2">進捗</div>
                      <div className="space-y-2">
                        <Progress
                          value={getProjectProgress(selectedProject)}
                          className="h-3"
                        />
                        <div className="text-sm text-neutral-600">
                          {getProjectProgress(selectedProject)}% 完了 (
                          {
                            getProjectTasks(selectedProject).filter(
                              (t) => t.status === "completed"
                            ).length
                          }{" "}
                          / {getProjectTasks(selectedProject).length} タスク)
                        </div>
                      </div>
                    </div>
                    <div>
                      <EditProjectDialog
                        project={selectedProject}
                        onProjectUpdate={(updatedProject) => {
                          onProjectUpdate(updatedProject);
                          setSelectedProject(updatedProject);
                        }}
                        trigger={
                          <Button variant="outline" className="w-full">
                            <Edit2 className="size-4 mr-2" />
                            編集
                          </Button>
                        }
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* プロジェクトのタスク */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">タスク一覧</CardTitle>
                    <CardDescription>
                      このプロジェクトに含まれるタスク (
                      {getProjectTasks(selectedProject).length}件)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {getProjectTasks(selectedProject).length === 0 ? (
                      <p className="text-center text-neutral-500 py-4">
                        タスクはありません
                      </p>
                    ) : (
                      <div className="space-y-2">
                        {getProjectTasks(selectedProject).map((task) => (
                          <div
                            key={task.id}
                            className="p-3 border rounded-lg hover:border-neutral-300 cursor-pointer transition-colors"
                            onClick={() => navigateTo("tasks", task.id)}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <span>{task.title}</span>
                                  {task.status === "completed" && (
                                    <Badge variant="secondary" className="text-xs">
                                      完了
                                    </Badge>
                                  )}
                                  {task.status === "todays" && (
                                    <Badge className="text-xs bg-blue-600">
                                      今日
                                    </Badge>
                                  )}
                                  {task.status === "progress" && (
                                    <Badge variant="outline" className="text-xs">
                                      進行中
                                    </Badge>
                                  )}
                                </div>
                                <p className="text-neutral-600 text-sm mt-1">
                                  {task.description}
                                </p>
                              </div>
                              <Button variant="ghost" size="sm">
                                <ExternalLink className="size-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="py-12">
                  <p className="text-center text-neutral-500">
                    プロジェクトを選択して詳細を表示
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}