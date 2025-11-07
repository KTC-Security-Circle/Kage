import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Tag as TagType, AppData } from "../App";
import { Tag as TagIcon, Hash, FileText, CheckSquare, FolderOpen, Edit2 } from "lucide-react";
import { CreateTagDialog } from "./CreateTagDialog";
import { EditTagDialog } from "./EditTagDialog";

type TagsScreenProps = {
  tags: TagType[];
  data: AppData;
  navigateTo: (screen: string, itemId?: string) => void;
  onTagCreate: (tag: TagType) => void;
  onTagUpdate: (tag: TagType) => void;
};

export function TagsScreen({ tags, data, navigateTo, onTagCreate, onTagUpdate }: TagsScreenProps) {
  const [selectedTag, setSelectedTag] = useState<TagType | null>(
    tags.length > 0 ? tags[0] : null
  );

  const getTaggedItems = (tagName: string) => {
    const memos = data.memos.filter((m) => m.tags.includes(tagName));
    const tasks = data.tasks.filter((t) => t.tags.includes(tagName));
    // プロジェクトはtagsプロパティを持たないため空配列
    const projects: typeof data.projects = [];
    return { memos, tasks, projects };
  };

  return (
    <div className="h-full flex flex-col">
      {/* ヘッダー */}
      <div className="p-6 border-b bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1>タグ</h1>
            <p className="text-neutral-600 mt-1">
              メモ、タスク、プロジェクトを整理するタグ ({tags.length}件)
            </p>
          </div>
          <div className="flex items-center gap-3">
            <CreateTagDialog onCreateTag={onTagCreate} />
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="flex-1 overflow-hidden p-6">
        <div className="h-full grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* タグ一覧 */}
          <div className="space-y-3 overflow-y-auto">
            {tags.length === 0 ? (
              <Card>
                <CardContent className="py-8">
                  <p className="text-center text-neutral-500">タグはありません</p>
                </CardContent>
              </Card>
            ) : (
              tags.map((tag) => {
                const { memos, tasks, projects } = getTaggedItems(tag.name);
                const totalCount = memos.length + tasks.length + projects.length;

                return (
                  <Card
                    key={tag.id}
                    className={`cursor-pointer transition-all ${
                      selectedTag?.id === tag.id
                        ? "border-blue-500 shadow-md"
                        : "hover:border-neutral-300"
                    }`}
                    onClick={() => setSelectedTag(tag)}
                  >
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: tag.color }}
                          />
                          <CardTitle className="text-base">{tag.name}</CardTitle>
                        </div>
                        <Badge variant="secondary">{totalCount}</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex gap-4 text-xs text-neutral-600">
                        <div className="flex items-center gap-1">
                          <FileText className="size-3" />
                          {memos.length} メモ
                        </div>
                        <div className="flex items-center gap-1">
                          <CheckSquare className="size-3" />
                          {tasks.length} タスク
                        </div>
                        <div className="flex items-center gap-1">
                          <FolderOpen className="size-3" />
                          {projects.length} PJ
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            )}
          </div>

          {/* タグの詳細 */}
          <div className="lg:col-span-2">
            {selectedTag ? (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div
                        className="w-8 h-8 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: selectedTag.color + "20" }}
                      >
                        <TagIcon className="size-5" style={{ color: selectedTag.color }} />
                      </div>
                      <div>
                        <CardTitle>{selectedTag.name}</CardTitle>
                        <CardDescription>
                          {getTaggedItems(selectedTag.name).memos.length +
                            getTaggedItems(selectedTag.name).tasks.length +
                            getTaggedItems(selectedTag.name).projects.length}{" "}
                          件のアイテム
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-end">
                      <EditTagDialog
                        tag={selectedTag}
                        onTagUpdate={onTagUpdate}
                        trigger={
                          <Button variant="outline">
                            <Edit2 className="size-4 mr-2" />
                            編集
                          </Button>
                        }
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* タグ付きメモ */}
                {getTaggedItems(selectedTag.name).memos.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <FileText className="size-5" />
                        メモ ({getTaggedItems(selectedTag.name).memos.length})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {getTaggedItems(selectedTag.name).memos.map((memo) => (
                          <div
                            key={memo.id}
                            className="p-3 border rounded-lg hover:border-neutral-300 cursor-pointer transition-colors"
                            onClick={() =>
                              navigateTo(
                                memo.status === "processing"
                                  ? "processing-memos"
                                  : "memo-history",
                                memo.id
                              )
                            }
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <span>{memo.title}</span>
                                  {memo.status === "processing" && (
                                    <Badge variant="outline" className="text-xs">
                                      処理中
                                    </Badge>
                                  )}
                                </div>
                                <p className="text-neutral-600 text-sm mt-1 line-clamp-1">
                                  {memo.content}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* タグ付きタスク */}
                {getTaggedItems(selectedTag.name).tasks.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <CheckSquare className="size-5" />
                        タスク ({getTaggedItems(selectedTag.name).tasks.length})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {getTaggedItems(selectedTag.name).tasks.map((task) => (
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
                                </div>
                                <p className="text-neutral-600 text-sm mt-1">
                                  {task.description}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* タグ付きプロジェクト */}
                {getTaggedItems(selectedTag.name).projects.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <FolderOpen className="size-5" />
                        プロジェクト ({getTaggedItems(selectedTag.name).projects.length})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {getTaggedItems(selectedTag.name).projects.map((project) => (
                          <div
                            key={project.id}
                            className="p-3 border rounded-lg hover:border-neutral-300 cursor-pointer transition-colors"
                            onClick={() => navigateTo("projects", project.id)}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <span>{project.title}</span>
                                  {project.status === "completed" && (
                                    <Badge variant="secondary" className="text-xs">
                                      完了
                                    </Badge>
                                  )}
                                  {project.status === "active" && (
                                    <Badge className="text-xs">進行中</Badge>
                                  )}
                                </div>
                                <p className="text-neutral-600 text-sm mt-1">
                                  {project.description}
                                </p>
                                <div className="text-xs text-neutral-500 mt-1">
                                  {data.tasks.filter((t) => t.projectId === project.id).length} タスク
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card>
                <CardContent className="py-12">
                  <p className="text-center text-neutral-500">
                    タグを選択して詳細を表示
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