import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { BookOpen, Search, ExternalLink, Tag as TagIcon, CheckCircle2, FileQuestion, XCircle, Edit2 } from "lucide-react";
import { Term, Tag, AppData } from "../App";
import { CreateTermDialog } from "./CreateTermDialog";
import { EditTermDialog } from "./EditTermDialog";

type TermsScreenProps = {
  terms: Term[];
  tags: Tag[];
  data: AppData;
  navigateTo: (screen: string, itemId?: string) => void;
  onTermCreate: (term: Term) => void;
  onTermUpdate: (term: Term) => void;
};

export function TermsScreen({ terms, tags, data, navigateTo, onTermCreate, onTermUpdate }: TermsScreenProps) {
  const [selectedTerm, setSelectedTerm] = useState<Term | null>(
    terms.length > 0 ? terms[0] : null
  );
  const [searchQuery, setSearchQuery] = useState("");

  const approvedTerms = terms.filter((t) => t.status === "approved");
  const draftTerms = terms.filter((t) => t.status === "draft");
  const deprecatedTerms = terms.filter((t) => t.status === "deprecated");

  const filterTerms = (termsList: Term[]) => {
    if (!searchQuery) return termsList;
    const query = searchQuery.toLowerCase();
    return termsList.filter(
      (term) =>
        term.title.toLowerCase().includes(query) ||
        term.key.toLowerCase().includes(query) ||
        term.description?.toLowerCase().includes(query) ||
        term.synonyms.some((s) => s.toLowerCase().includes(query))
    );
  };

  const getStatusIcon = (status: Term["status"]) => {
    switch (status) {
      case "approved":
        return <CheckCircle2 className="size-4 text-slate-900" />;
      case "draft":
        return <FileQuestion className="size-4 text-slate-900" />;
      case "deprecated":
        return <XCircle className="size-4 text-slate-900" />;
    }
  };

  const getStatusBadge = (status: Term["status"]) => {
    switch (status) {
      case "approved":
        return <Badge className="bg-blue-600">承認済み</Badge>;
      case "draft":
        return <Badge variant="outline" className="border-slate-600 text-slate-600">草案</Badge>;
      case "deprecated":
        return <Badge variant="outline" className="border-slate-600 text-slate-600">非推奨</Badge>;
    }
  };

  const renderTermCard = (term: Term) => {
    return (
      <Card
        key={term.id}
        className={`cursor-pointer transition-all ${
          selectedTerm?.id === term.id
            ? "border-blue-500 shadow-md"
            : "hover:border-neutral-300"
        }`}
        onClick={() => setSelectedTerm(term)}
      >
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                {getStatusIcon(term.status)}
                <CardTitle className="text-base">{term.title}</CardTitle>
              </div>
              <CardDescription className="text-xs mt-1">
                キー: {term.key}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-neutral-600 line-clamp-2">
            {term.description || "説明なし"}
          </p>
          {term.synonyms.length > 0 && (
            <div className="mt-2 flex gap-1 flex-wrap">
              {term.synonyms.slice(0, 3).map((synonym, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs">
                  {synonym}
                </Badge>
              ))}
              {term.synonyms.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{term.synonyms.length - 3}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* ヘッダー */}
      <div className="p-6 border-b bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1>社内用語管理</h1>
            <p className="text-neutral-600 mt-1">
              社内固有の用語・略語・定義を管理 ({terms.length}件)
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* 検索バー */}
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 size-4 text-neutral-400" />
              <Input
                placeholder="用語、キー、同義語で検索..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <CreateTermDialog onCreateTerm={onTermCreate} tags={tags} />
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="flex-1 overflow-hidden p-6">
        <div className="h-full grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 用語一覧 */}
          <div className="space-y-3">
            <Tabs defaultValue="approved">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="approved">
                  承認 ({approvedTerms.length})
                </TabsTrigger>
                <TabsTrigger value="draft">
                  草案 ({draftTerms.length})
                </TabsTrigger>
                <TabsTrigger value="deprecated">
                  非推奨 ({deprecatedTerms.length})
                </TabsTrigger>
              </TabsList>

              <TabsContent value="approved" className="space-y-3 mt-3">
                {filterTerms(approvedTerms).length === 0 ? (
                  <Card>
                    <CardContent className="py-8">
                      <p className="text-center text-neutral-500">
                        承認済みの用語はありません
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  filterTerms(approvedTerms).map((term) => renderTermCard(term))
                )}
              </TabsContent>

              <TabsContent value="draft" className="space-y-3 mt-3">
                {filterTerms(draftTerms).length === 0 ? (
                  <Card>
                    <CardContent className="py-8">
                      <p className="text-center text-neutral-500">
                        草案の用語はありません
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  filterTerms(draftTerms).map((term) => renderTermCard(term))
                )}
              </TabsContent>

              <TabsContent value="deprecated" className="space-y-3 mt-3">
                {filterTerms(deprecatedTerms).length === 0 ? (
                  <Card>
                    <CardContent className="py-8">
                      <p className="text-center text-neutral-500">
                        非推奨の用語はありません
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  filterTerms(deprecatedTerms).map((term) => renderTermCard(term))
                )}
              </TabsContent>
            </Tabs>
          </div>

          {/* 用語の詳細 */}
          <div className="lg:col-span-2">
            {selectedTerm ? (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <BookOpen className="size-6 text-blue-600" />
                          <div>
                            <CardTitle>{selectedTerm.title}</CardTitle>
                            <CardDescription className="mt-1">
                              キー: <code className="text-xs bg-neutral-100 px-1 py-0.5 rounded">{selectedTerm.key}</code>
                            </CardDescription>
                          </div>
                        </div>
                      </div>
                      {getStatusBadge(selectedTerm.status)}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* 説明 */}
                    <div>
                      <div className="text-sm text-neutral-500 mb-2">説明</div>
                      <p className="text-neutral-700">
                        {selectedTerm.description || "説明が登録されていません"}
                      </p>
                    </div>

                    {/* 同義語 */}
                    {selectedTerm.synonyms.length > 0 && (
                      <div>
                        <div className="text-sm text-neutral-500 mb-2">同義語</div>
                        <div className="flex gap-2 flex-wrap">
                          {selectedTerm.synonyms.map((synonym, idx) => (
                            <Badge key={idx} variant="secondary">
                              {synonym}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* タグ */}
                    {selectedTerm.tags.length > 0 && (
                      <div>
                        <div className="text-sm text-neutral-500 mb-2">タグ</div>
                        <div className="flex gap-2 flex-wrap">
                          {selectedTerm.tags.map((tagName) => {
                            const tag = tags.find((t) => t.name === tagName);
                            return (
                              <Badge
                                key={tagName}
                                variant="outline"
                                className="cursor-pointer"
                                style={{
                                  borderColor: tag?.color,
                                  color: tag?.color,
                                }}
                                onClick={() => navigateTo("tags", tag?.id)}
                              >
                                <TagIcon className="size-3 mr-1" />
                                {tagName}
                              </Badge>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* 出典URL */}
                    {selectedTerm.sourceUrl && (
                      <div>
                        <div className="text-sm text-neutral-500 mb-2">出典</div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open(selectedTerm.sourceUrl, "_blank")}
                        >
                          <ExternalLink className="size-4 mr-2" />
                          外部リンクを開く
                        </Button>
                      </div>
                    )}

                    {/* メタデータ */}
                    <div className="pt-4 border-t">
                      <div className="grid grid-cols-2 gap-4 text-xs text-neutral-500">
                        <div>
                          <div>作成日</div>
                          <div className="text-neutral-700 mt-1">
                            {selectedTerm.createdAt.toLocaleDateString("ja-JP")}
                          </div>
                        </div>
                        <div>
                          <div>最終更新</div>
                          <div className="text-neutral-700 mt-1">
                            {selectedTerm.updatedAt.toLocaleDateString("ja-JP")}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* 編集ボタン */}
                    <div>
                      <EditTermDialog
                        term={selectedTerm}
                        tags={tags}
                        onTermUpdate={(updatedTerm) => {
                          onTermUpdate(updatedTerm);
                          setSelectedTerm(updatedTerm);
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

                {/* 関連するメモ・タスク */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">関連アイテム</CardTitle>
                    <CardDescription>
                      この用語に関連するタグを持つメモとタスク
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* 関連メモ */}
                    {(() => {
                      const relatedMemos = data.memos.filter((memo) =>
                        memo.tags.some((tag) => selectedTerm.tags.includes(tag))
                      );
                      return relatedMemos.length > 0 ? (
                        <div>
                          <div className="text-sm text-neutral-500 mb-2">
                            関連メモ ({relatedMemos.length})
                          </div>
                          <div className="space-y-2">
                            {relatedMemos.slice(0, 3).map((memo) => (
                              <div
                                key={memo.id}
                                className="p-2 border rounded-lg hover:border-neutral-300 cursor-pointer transition-colors text-sm"
                                onClick={() =>
                                  navigateTo(
                                    memo.status === "inbox"
                                      ? "inbox-memos"
                                      : memo.status === "active"
                                        ? "active-memos"
                                        : memo.status === "idea"
                                          ? "idea-memos"
                                          : "archive-memos",
                                    memo.id
                                  )
                                }
                              >
                                {memo.title}
                              </div>
                            ))}
                            {relatedMemos.length > 3 && (
                              <p className="text-xs text-neutral-500">
                                他 {relatedMemos.length - 3} 件
                              </p>
                            )}
                          </div>
                        </div>
                      ) : null;
                    })()}

                    {/* 関連タスク */}
                    {(() => {
                      const relatedTasks = data.tasks.filter((task) =>
                        task.tags.some((tag) => selectedTerm.tags.includes(tag))
                      );
                      return relatedTasks.length > 0 ? (
                        <div>
                          <div className="text-sm text-neutral-500 mb-2">
                            関連タスク ({relatedTasks.length})
                          </div>
                          <div className="space-y-2">
                            {relatedTasks.slice(0, 3).map((task) => (
                              <div
                                key={task.id}
                                className="p-2 border rounded-lg hover:border-neutral-300 cursor-pointer transition-colors text-sm flex items-center justify-between"
                                onClick={() => navigateTo("tasks", task.id)}
                              >
                                <span>{task.title}</span>
                                {task.status === "completed" && (
                                  <Badge variant="secondary" className="text-xs">
                                    完了
                                  </Badge>
                                )}
                              </div>
                            ))}
                            {relatedTasks.length > 3 && (
                              <p className="text-xs text-neutral-500">
                                他 {relatedTasks.length - 3} 件
                              </p>
                            )}
                          </div>
                        </div>
                      ) : null;
                    })()}

                    {data.memos.filter((memo) =>
                      memo.tags.some((tag) => selectedTerm.tags.includes(tag))
                    ).length === 0 &&
                      data.tasks.filter((task) =>
                        task.tags.some((tag) => selectedTerm.tags.includes(tag))
                      ).length === 0 && (
                        <p className="text-center text-neutral-500 py-4">
                          関連するアイテムはありません
                        </p>
                      )}
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card>
                <CardContent className="py-12">
                  <p className="text-center text-neutral-500">
                    用語を選択して詳細を表示
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