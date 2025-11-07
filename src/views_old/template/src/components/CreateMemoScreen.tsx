import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Memo, Tag } from "../App";
import { ArrowLeft, Save, Eye, Edit3, X, Tag as TagIcon } from "lucide-react";

type CreateMemoScreenProps = {
  tags: Tag[];
  navigateTo: (screen: string, itemId?: string) => void;
  onMemoCreate: (memo: Memo) => void;
  initialStatus?: Memo["status"];
};

export function CreateMemoScreen({
  tags,
  navigateTo,
  onMemoCreate,
  initialStatus = "inbox",
}: CreateMemoScreenProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [status, setStatus] = useState<Memo["status"]>(initialStatus);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"edit" | "preview">("edit");

  const handleCreate = () => {
    if (!title.trim() || !content.trim()) {
      alert("タイトルと内容は必須です");
      return;
    }

    const newMemo: Memo = {
      id: `memo-${Date.now()}`,
      title: title.trim(),
      content: content.trim(),
      status: status,
      tags: selectedTags,
      createdAt: new Date(),
      updatedAt: new Date(),
      aiSuggestionStatus: "not_requested",
    };

    onMemoCreate(newMemo);

    // メモ画面に遷移
    navigateTo("memos", newMemo.id);
  };

  const handleCancel = () => {
    if (title || content) {
      if (confirm("入力内容が失われますがよろしいですか？")) {
        navigateTo("home");
      }
    } else {
      navigateTo("home");
    }
  };

  const toggleTag = (tagName: string) => {
    if (selectedTags.includes(tagName)) {
      setSelectedTags(selectedTags.filter((t) => t !== tagName));
    } else {
      setSelectedTags([...selectedTags, tagName]);
    }
  };

  // シンプルなマークダウンプレビュー
  const renderMarkdownPreview = (markdown: string) => {
    if (!markdown) {
      return <p className="text-neutral-400 italic">プレビューはこちらに表示されます</p>;
    }

    const lines = markdown.split("\n");
    return lines.map((line, idx) => {
      // 見出し
      if (line.startsWith("### ")) {
        return <h3 key={idx} className="mt-4 mb-2">{line.replace("### ", "")}</h3>;
      }
      if (line.startsWith("## ")) {
        return <h2 key={idx} className="mt-4 mb-2">{line.replace("## ", "")}</h2>;
      }
      if (line.startsWith("# ")) {
        return <h1 key={idx} className="mt-4 mb-2">{line.replace("# ", "")}</h1>;
      }

      // リスト
      if (line.startsWith("- ") || line.startsWith("* ")) {
        return <li key={idx} className="ml-4">{line.replace(/^[-*] /, "")}</li>;
      }

      // コードブロック（簡易版）
      if (line.startsWith("```")) {
        return <div key={idx} className="bg-neutral-100 p-2 rounded my-2 text-sm font-mono">{line.replace(/```/g, "")}</div>;
      }

      // 太字
      let processedLine = line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      processedLine = processedLine.replace(/__(.*?)__/g, "<strong>$1</strong>");

      // イタリック
      processedLine = processedLine.replace(/\*(.*?)\*/g, "<em>$1</em>");
      processedLine = processedLine.replace(/_(.*?)_/g, "<em>$1</em>");

      // インラインコード
      processedLine = processedLine.replace(/`(.*?)`/g, "<code class='bg-neutral-100 px-1 py-0.5 rounded text-sm'>$1</code>");

      // 空行
      if (line.trim() === "") {
        return <br key={idx} />;
      }

      return <p key={idx} className="mb-2" dangerouslySetInnerHTML={{ __html: processedLine }} />;
    });
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* ヘッダー */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={handleCancel}>
                <ArrowLeft className="size-4 mr-2" />
                戻る
              </Button>
              <div>
                <h1 className="text-xl">新しいメモを作成</h1>
                <p className="text-sm text-neutral-600">マークダウン形式で記述できます</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={handleCancel}>
                キャンセル
              </Button>
              <Button onClick={handleCreate} disabled={!title.trim() || !content.trim()}>
                <Save className="size-4 mr-2" />
                保存
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* メインコンテンツ */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左側：入力フォーム */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>基本情報</CardTitle>
                <CardDescription>メモのタイトルとステータスを設定</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="memo-title">
                    タイトル <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="memo-title"
                    placeholder="メモのタイトルを入力..."
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="text-lg"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="memo-status">ステータス</Label>
                  <Select value={status} onValueChange={(value) => setStatus(value as Memo["status"])}>
                    <SelectTrigger id="memo-status">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="inbox">INBOX</SelectItem>
                      <SelectItem value="active">ACTIVE</SelectItem>
                      <SelectItem value="idea">IDEA</SelectItem>
                      <SelectItem value="archive">ARCHIVE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>内容</CardTitle>
                <CardDescription>マークダウン形式で記述できます</CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "edit" | "preview")}>
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="edit" className="flex items-center gap-2">
                      <Edit3 className="size-4" />
                      編集
                    </TabsTrigger>
                    <TabsTrigger value="preview" className="flex items-center gap-2">
                      <Eye className="size-4" />
                      プレビュー
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="edit" className="mt-4">
                    <Textarea
                      placeholder="# 見出し&#10;&#10;ここに内容を入力...&#10;&#10;## サブ見出し&#10;&#10;- リスト項目1&#10;- リスト項目2&#10;&#10;**太字** や *イタリック* や `コード` が使えます。"
                      value={content}
                      onChange={(e) => setContent(e.target.value)}
                      rows={20}
                      className="resize-none font-mono text-sm"
                    />
                    <div className="mt-2 text-xs text-neutral-500">
                      <p>マークダウン記法:</p>
                      <ul className="mt-1 space-y-1">
                        <li>• 見出し: # H1, ## H2, ### H3</li>
                        <li>• リスト: - または *</li>
                        <li>• 太字: **text** または __text__</li>
                        <li>• イタリック: *text* または _text_</li>
                        <li>• コード: `code`</li>
                      </ul>
                    </div>
                  </TabsContent>

                  <TabsContent value="preview" className="mt-4">
                    <div className="min-h-[500px] p-4 border rounded-lg bg-white prose prose-sm max-w-none">
                      {title && <h1 className="mb-4">{title}</h1>}
                      {renderMarkdownPreview(content)}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* 右側：タグ選択とヒント */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TagIcon className="size-5" />
                  タグ
                </CardTitle>
                <CardDescription>メモにタグを付けて整理</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {tags.length === 0 ? (
                  <p className="text-sm text-neutral-500">タグがありません</p>
                ) : (
                  <div className="flex gap-2 flex-wrap">
                    {tags.map((tag) => (
                      <Badge
                        key={tag.id}
                        variant={selectedTags.includes(tag.name) ? "default" : "outline"}
                        className="cursor-pointer transition-all"
                        style={
                          selectedTags.includes(tag.name)
                            ? { backgroundColor: tag.color, borderColor: tag.color }
                            : { borderColor: tag.color, color: tag.color }
                        }
                        onClick={() => toggleTag(tag.name)}
                      >
                        {tag.name}
                      </Badge>
                    ))}
                  </div>
                )}

                {selectedTags.length > 0 && (
                  <div className="pt-4 border-t">
                    <p className="text-sm text-neutral-500 mb-2">選択中のタグ:</p>
                    <div className="flex gap-2 flex-wrap">
                      {selectedTags.map((tagName) => {
                        const tag = tags.find((t) => t.name === tagName);
                        return (
                          <Badge
                            key={tagName}
                            style={{ backgroundColor: tag?.color }}
                            className="gap-1"
                          >
                            {tagName}
                            <button
                              onClick={() => toggleTag(tagName)}
                              className="ml-1 hover:text-red-200"
                            >
                              <X className="size-3" />
                            </button>
                          </Badge>
                        );
                      })}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>ステータスの説明</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div>
                  <div className="font-medium text-blue-600">INBOX</div>
                  <p className="text-neutral-600">
                    未処理のメモ。後でレビューしてアクションを決定します。
                  </p>
                </div>
                <div>
                  <div className="font-medium text-green-600">ACTIVE</div>
                  <p className="text-neutral-600">
                    現在進行中のプロジェクトや作業に関連するメモ。
                  </p>
                </div>
                <div>
                  <div className="font-medium text-purple-600">IDEA</div>
                  <p className="text-neutral-600">
                    将来のアイデアや参考資料として保存。
                  </p>
                </div>
                <div>
                  <div className="font-medium text-neutral-600">ARCHIVE</div>
                  <p className="text-neutral-600">
                    完了または不要になったメモのアーカイブ。
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-blue-50 border-blue-200">
              <CardHeader>
                <CardTitle className="text-sm">💡 ヒント</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-neutral-700">
                <p>• まずはINBOXに保存し、後で整理することもできます</p>
                <p>• プレビュータブで表示を確認できます</p>
                <p>• タグを使って関連するメモをグループ化できます</p>
                <p>• 長文の場合は見出しを使って構造化すると読みやすくなります</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}