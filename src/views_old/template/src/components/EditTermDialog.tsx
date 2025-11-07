import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Term, Tag } from "../App";
import { Save, BookOpen, X } from "lucide-react";
import { Badge } from "./ui/badge";

type EditTermDialogProps = {
  term: Term;
  tags: Tag[];
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  onTermUpdate: (term: Term) => void;
  trigger?: React.ReactNode;
};

export function EditTermDialog({
  term,
  tags,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
  onTermUpdate,
  trigger,
}: EditTermDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const open = controlledOpen !== undefined ? controlledOpen : internalOpen;
  const setOpen = controlledOnOpenChange || setInternalOpen;

  const [key, setKey] = useState(term.key);
  const [title, setTitle] = useState(term.title);
  const [description, setDescription] = useState(term.description || "");
  const [status, setStatus] = useState<Term["status"]>(term.status);
  const [sourceUrl, setSourceUrl] = useState(term.sourceUrl || "");
  const [synonymInput, setSynonymInput] = useState("");
  const [synonyms, setSynonyms] = useState<string[]>(term.synonyms);
  const [selectedTags, setSelectedTags] = useState<string[]>(term.tags);

  useEffect(() => {
    if (open) {
      setKey(term.key);
      setTitle(term.title);
      setDescription(term.description || "");
      setStatus(term.status);
      setSourceUrl(term.sourceUrl || "");
      setSynonyms(term.synonyms);
      setSelectedTags(term.tags);
      setSynonymInput("");
    }
  }, [open, term]);

  const handleUpdate = () => {
    if (!key.trim() || !title.trim()) return;

    const updatedTerm: Term = {
      ...term,
      key: key.trim().toUpperCase().replace(/\s+/g, "_"),
      title: title.trim(),
      description: description.trim() || undefined,
      status: status,
      sourceUrl: sourceUrl.trim() || undefined,
      synonyms: synonyms,
      tags: selectedTags,
      updatedAt: new Date(),
    };

    onTermUpdate(updatedTerm);
    setOpen(false);
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
        {trigger || <Button>編集</Button>}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookOpen className="size-5" />
            用語を編集
          </DialogTitle>
          <DialogDescription>
            社内用語の詳細を編集してください。
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="edit-term-key">
                キー <span className="text-red-500">*</span>
              </Label>
              <Input
                id="edit-term-key"
                placeholder="例: GTD, API, CI_CD"
                value={key}
                onChange={(e) => setKey(e.target.value)}
              />
              <p className="text-xs text-neutral-500">
                スペースはアンダースコアに変換されます
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-term-status">ステータス</Label>
              <Select value={status} onValueChange={(value) => setStatus(value as Term["status"])}>
                <SelectTrigger id="edit-term-status">
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
            <Label htmlFor="edit-term-title">
              タイトル <span className="text-red-500">*</span>
            </Label>
            <Input
              id="edit-term-title"
              placeholder="例: Getting Things Done"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-term-description">説明（任意）</Label>
            <Textarea
              id="edit-term-description"
              placeholder="用語の意味や使い方を入力..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="resize-none"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-term-source-url">出典URL（任意）</Label>
            <Input
              id="edit-term-source-url"
              type="url"
              placeholder="https://example.com"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-term-synonym">同義語（任意）</Label>
            <div className="flex gap-2">
              <Input
                id="edit-term-synonym"
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
            onClick={() => setOpen(false)}
          >
            キャンセル
          </Button>
          <Button onClick={handleUpdate} disabled={!key.trim() || !title.trim()}>
            <Save className="size-4 mr-2" />
            更新
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}