import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Term, Tag } from "../App";
import { Plus, BookOpen, X } from "lucide-react";
import { Badge } from "./ui/badge";

type CreateTermDialogProps = {
  onCreateTerm: (term: Term) => void;
  tags: Tag[];
  trigger?: React.ReactNode;
};

export function CreateTermDialog({
  onCreateTerm,
  tags,
  trigger,
}: CreateTermDialogProps) {
  const [open, setOpen] = useState(false);
  const [key, setKey] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<Term["status"]>("draft");
  const [sourceUrl, setSourceUrl] = useState("");
  const [synonymInput, setSynonymInput] = useState("");
  const [synonyms, setSynonyms] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const handleCreate = () => {
    if (!key.trim() || !title.trim()) return;

    const newTerm: Term = {
      id: `term-${Date.now()}`,
      key: key.trim().toUpperCase().replace(/\s+/g, "_"),
      title: title.trim(),
      description: description.trim() || undefined,
      status: status,
      sourceUrl: sourceUrl.trim() || undefined,
      synonyms: synonyms,
      tags: selectedTags,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    onCreateTerm(newTerm);
    resetForm();
    setOpen(false);
  };

  const resetForm = () => {
    setKey("");
    setTitle("");
    setDescription("");
    setStatus("draft");
    setSourceUrl("");
    setSynonymInput("");
    setSynonyms([]);
    setSelectedTags([]);
  };

  const addSynonym = () => {
    const synonym = synonymInput.trim();
    if (synonym && !synonyms.includes(synonym)) {
      setSynonyms([...synonyms, synonym]);
      setSynonymInput("");
    }
  };

  const removeSynonym = (synonym: string) => {
    setSynonyms(synonyms.filter((s) => s !== synonym));
  };

  const toggleTag = (tagName: string) => {
    if (selectedTags.includes(tagName)) {
      setSelectedTags(selectedTags.filter((t) => t !== tagName));
    } else {
      setSelectedTags([...selectedTags, tagName]);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="size-4 mr-2" />
            新しい用語
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookOpen className="size-5" />
            新しい用語を作成
          </DialogTitle>
          <DialogDescription>
            社内用語の詳細を入力してください。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="term-key">
                キー <span className="text-red-500">*</span>
              </Label>
              <Input
                id="term-key"
                placeholder="例: GTD, API, CI_CD"
                value={key}
                onChange={(e) => setKey(e.target.value)}
              />
              <p className="text-xs text-neutral-500">
                スペースはアンダースコアに変換されます
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="term-status">ステータス</Label>
              <Select value={status} onValueChange={(value) => setStatus(value as Term["status"])}>
                <SelectTrigger id="term-status">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">草案</SelectItem>
                  <SelectItem value="approved">承認済み</SelectItem>
                  <SelectItem value="deprecated">非推奨</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="term-title">
              タイトル <span className="text-red-500">*</span>
            </Label>
            <Input
              id="term-title"
              placeholder="例: Getting Things Done"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="term-description">説明（任意）</Label>
            <Textarea
              id="term-description"
              placeholder="用語の意味や使い方を入力..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="term-source-url">出典URL（任意）</Label>
            <Input
              id="term-source-url"
              type="url"
              placeholder="https://example.com"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="term-synonym">同義語（任意）</Label>
            <div className="flex gap-2">
              <Input
                id="term-synonym"
                placeholder="同義語を入力してEnter"
                value={synonymInput}
                onChange={(e) => setSynonymInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addSynonym();
                  }
                }}
              />
              <Button type="button" variant="outline" onClick={addSynonym}>
                追加
              </Button>
            </div>
            {synonyms.length > 0 && (
              <div className="flex gap-2 flex-wrap mt-2">
                {synonyms.map((synonym) => (
                  <Badge key={synonym} variant="secondary" className="gap-1">
                    {synonym}
                    <button
                      type="button"
                      onClick={() => removeSynonym(synonym)}
                      className="ml-1 hover:text-red-600"
                    >
                      <X className="size-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-2">
            <Label>タグ（任意）</Label>
            <div className="border rounded-lg p-3 max-h-32 overflow-y-auto">
              {tags.length === 0 ? (
                <p className="text-sm text-neutral-500">タグがありません</p>
              ) : (
                <div className="flex gap-2 flex-wrap">
                  {tags.map((tag) => (
                    <Badge
                      key={tag.id}
                      variant={selectedTags.includes(tag.name) ? "default" : "outline"}
                      className="cursor-pointer"
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
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              setOpen(false);
              resetForm();
            }}
          >
            キャンセル
          </Button>
          <Button onClick={handleCreate} disabled={!key.trim() || !title.trim()}>
            <Plus className="size-4 mr-2" />
            用語を作成
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
