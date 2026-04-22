<template>
  <div class="book-detail-page">
    <section class="book-detail-page__topbar">
      <Button variant="ghost" @click="goBack">返回书架</Button>
      <span class="book-detail-page__crumb">Book ID: {{ bookId }}</span>
    </section>

    <section v-if="loading" class="book-detail-page__loading">
      <div class="book-detail-page__loading-card detail-card">
        <div class="space-y-3">
          <Skeleton v-for="i in 4" :key="i" class="h-4 w-full" />
          <Skeleton v-for="i in 3" :key="i+4" class="h-4 w-3/4" />
        </div>
      </div>
      <div class="book-detail-page__loading-card detail-card">
        <div class="space-y-3">
          <Skeleton v-for="i in 8" :key="i" class="h-4 w-full" />
        </div>
      </div>
    </section>

    <page-status-panel
      v-else-if="pageError"
      variant="error"
      title="书籍详情暂时无法加载"
      :description="pageError"
    >
      <template #action>
        <Button @click="reloadPage">重新加载</Button>
      </template>
    </page-status-panel>

    <template v-else-if="book">
      <section class="detail-hero">
        <div class="detail-hero__cover" :class="{ 'detail-hero__cover--filled': !!book.cover_url }">
          <img
            v-if="resolvedCoverUrl"
            class="detail-hero__cover-image"
            :src="resolvedCoverUrl"
            :alt="`${book.title} 封面`"
          />
          <template v-else>
            <div class="detail-hero__cover-badge">TXT</div>
            <div class="detail-hero__cover-letter">{{ getCoverLetter(book.title) }}</div>
          </template>
        </div>

        <div class="detail-hero__body">
          <div class="detail-hero__eyebrow">Book Detail</div>
          <h1 class="detail-hero__title">{{ book.title }}</h1>
          <p class="detail-hero__author">{{ book.author || "作者未填写" }}</p>
          <p class="detail-hero__description">
            {{
              book.description ||
              "这本书还没有补充简介，你可以先查看目录、继续阅读，或切换目录规则后重新解析。"
            }}
          </p>

          <div class="detail-hero__tags">
            <Badge variant="secondary">总章节 {{ formatNumber(book.total_chapters) }}</Badge>
            <Badge variant="secondary">总字数 {{ formatWordCount(book.total_words) }}</Badge>
            <Badge variant="secondary">当前规则 {{ currentRuleName }}</Badge>
            <Badge variant="secondary">{{ progressTagLabel }}</Badge>
            <Badge variant="secondary">{{ progressPercentLabel }}</Badge>
          </div>

          <div class="detail-hero__actions">
            <Button size="lg" :disabled="readingPending" @click="handleReadAction">
              {{ readActionLabel }}
            </Button>
            <Button variant="ghost" size="lg" @click="openCatalog">
              查看目录
            </Button>
            <Button variant="outline" size="lg" @click="openEditor">
              编辑信息
            </Button>
          </div>
        </div>
      </section>

      <section class="detail-grid">
        <div class="detail-card">
          <div class="detail-card__header">
            <span class="detail-card__heading">阅读信息</span>
          </div>

          <div class="detail-info-grid">
            <div class="detail-info-item">
              <span>作者</span>
              <strong>{{ book.author || "未填写" }}</strong>
            </div>
            <div class="detail-info-item">
              <span>阅读进度</span>
              <strong>{{ progressPercentLabel }}</strong>
            </div>
            <div class="detail-info-item">
              <span>最近阅读</span>
              <strong>{{ formatOptionalDate(book.recent_read_at) }}</strong>
            </div>
            <div class="detail-info-item">
              <span>阅读定位</span>
              <strong>{{ progressTagLabel }}</strong>
            </div>
            <div class="detail-info-item detail-info-item--wide">
              <span>简介</span>
              <strong class="detail-info-item__multiline">
                {{ book.description || "暂无简介" }}
              </strong>
            </div>
          </div>

          <div class="detail-group-list">
            <span class="detail-group-list__label">分组</span>
            <div class="detail-group-list__tags">
              <Badge v-for="group in book.groups" :key="group.id" variant="secondary">
                {{ group.name }}
              </Badge>
            </div>
          </div>
        </div>

        <div class="detail-card">
          <div class="detail-card__header">
            <span class="detail-card__heading">文件信息</span>
          </div>

          <div class="detail-info-grid">
            <div class="detail-info-item">
              <span>文件名</span>
              <strong>{{ book.file_name }}</strong>
            </div>
            <div class="detail-info-item">
              <span>编码</span>
              <strong>{{ book.encoding }}</strong>
            </div>
            <div class="detail-info-item">
              <span>收录时间</span>
              <strong>{{ formatDate(book.created_at) }}</strong>
            </div>
            <div class="detail-info-item">
              <span>更新时间</span>
              <strong>{{ formatDate(book.updated_at) }}</strong>
            </div>
          </div>

          <div class="detail-file-path">
            <span class="detail-file-path__label">本地文件</span>
            <code>{{ book.file_path }}</code>
          </div>
        </div>

        <div class="detail-card detail-card--full">
          <div class="detail-card__header">
            <span class="detail-card__heading">目录规则</span>
          </div>

          <div class="detail-rule-card">
            <div class="detail-rule-card__current">
              <span>当前使用</span>
              <strong>{{ currentRuleName }}</strong>
              <p>{{ currentRuleDescription }}</p>
            </div>

            <Alert v-if="rulesError" variant="warning" class="detail-rule-card__alert">
              {{ rulesError }}
            </Alert>

            <div class="detail-rule-card__actions">
              <Select v-model="selectedRuleId" :disabled="reparsePending || ruleOptions.length === 0">
                <SelectTrigger>
                  <SelectValue placeholder="选择目录规则" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="opt in ruleOptions" :key="opt.value" :value="String(opt.value)">
                    {{ opt.label }}
                  </SelectItem>
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                :disabled="reparsePending || !selectedRuleId"
                @click="handleReparse"
              >
                重新解析目录
              </Button>
            </div>
          </div>
        </div>
      </section>

      <Dialog :open="editorVisible" @update:open="editorVisible = $event">
      <DialogContent class="metadata-modal max-w-3xl">
        <div class="metadata-modal__layout">
          <div class="metadata-modal__cover-panel">
            <div class="metadata-modal__cover" :class="{ 'metadata-modal__cover--filled': !!book.cover_url }">
              <img
                v-if="resolvedCoverUrl"
                class="metadata-modal__cover-image"
                :src="resolvedCoverUrl"
                :alt="`${book.title} 封面`"
              />
              <template v-else>
                <span class="metadata-modal__cover-type">TXT</span>
                <strong class="metadata-modal__cover-letter">{{ getCoverLetter(book.title) }}</strong>
                <span class="metadata-modal__cover-text">无封面</span>
              </template>
            </div>

            <div class="metadata-modal__cover-actions">
              <input
                ref="coverInputRef"
                type="file"
                accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
                class="sr-only"
                @change="handleCoverUpload"
              />
              <Button variant="outline" :disabled="coverUploading" @click="coverInputRef?.click()">
                上传封面
              </Button>
              <Button
                v-if="book.cover_url"
                variant="ghost"
                class="text-red-600 hover:text-red-700"
                :disabled="coverDeleting"
                @click="handleRemoveCover"
              >
                删除封面
              </Button>
            </div>
          </div>

          <div class="metadata-modal__form">
            <label class="metadata-modal__field">
              <span>书名</span>
              <Input v-model="editableTitle" placeholder="用于全局显示的书名" />
            </label>

            <label class="metadata-modal__field">
              <span>作者</span>
              <Input v-model="editableAuthor" placeholder="作者可留空" />
            </label>

            <label class="metadata-modal__field">
              <span>简介</span>
              <textarea
                v-model="editableDescription"
                placeholder="支持多行简介"
                rows="6"
                class="metadata-modal__textarea"
              ></textarea>
            </label>
          </div>
        </div>

        <div class="metadata-modal__footer">
          <Button variant="ghost" @click="editorVisible = false">取消</Button>
          <Button :disabled="metadataSaving" @click="handleSaveMetadata">
            保存修改
          </Button>
        </div>
      </DialogContent>
    </Dialog>

      <chapter-catalog-modal-drawer
        v-model:show="catalogVisible"
        :book-title="book.title"
        :chapter-count="book.total_chapters"
        :chapters="chapters"
        @select="handleCatalogSelect"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRouter } from "vue-router";
import {
  Dialog,
  DialogContent,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { notify } from "@/utils/notify";


import { booksApi } from "../api/books";
import { resolveApiAssetUrl, ApiError, getErrorMessage } from "../api/client";
import { chapterRulesApi } from "../api/chapter-rules";
import ChapterCatalogModalDrawer from "../components/ChapterCatalogModalDrawer.vue";
import PageStatusPanel from "../components/PageStatusPanel.vue";
import type { BookChapter, BookDetail, ChapterRule, ReadingProgress } from "../types/api";
import { formatDateTime, formatNumber, formatPercent, formatWordCount } from "../utils/format";
import { useBooksCacheStore } from "../stores/booksCache";

const props = defineProps<{
  bookId: number;
}>();

const router = useRouter();
const booksCacheStore = useBooksCacheStore();

const BOOK_METADATA_UPDATED_EVENT = "books:metadata-updated";
const book = ref<BookDetail | null>(null);
const chapters = ref<BookChapter[]>([]);
const rules = ref<ChapterRule[]>([]);
const progress = ref<ReadingProgress | null>(null);
const selectedRuleId = ref<number | null>(null);
const loading = ref(true);
const pageError = ref<string | null>(null);
const rulesError = ref<string | null>(null);
const readingPending = ref(false);
const reparsePending = ref(false);
const editorVisible = ref(false);
const metadataSaving = ref(false);
const coverUploading = ref(false);
const coverDeleting = ref(false);
const catalogVisible = ref(false);
const editableTitle = ref("");
const editableAuthor = ref("");
const editableDescription = ref("");

const ruleOptions = computed(() => {
  return rules.value.map((rule) => ({
    label: rule.is_builtin ? `${rule.rule_name}（内置）` : rule.rule_name,
    value: rule.id,
  }));
});

const currentRuleName = computed(() => {
  if (book.value?.chapter_rule?.rule_name) {
    return book.value.chapter_rule.rule_name;
  }

  const selectedRule = rules.value.find((rule) => rule.id === selectedRuleId.value);
  return selectedRule?.rule_name || "未指定";
});

const currentRuleDescription = computed(() => {
  if (book.value?.chapter_rule?.description) {
    return book.value.chapter_rule.description;
  }

  const selectedRule = rules.value.find((rule) => rule.id === selectedRuleId.value);
  return selectedRule?.description || "你可以在这里切换规则，并重新解析当前书籍的目录。";
});

const readActionLabel = computed(() => {
  return progress.value ? "继续阅读" : "开始阅读";
});

const progressTagLabel = computed(() => {
  if (!progress.value) {
    return "尚未开始";
  }

  return `上次读到第 ${formatNumber(progress.value.chapter_index + 1)} 章`;
});

const progressPercentLabel = computed(() => {
  return `进度 ${formatPercent(book.value?.progress_percent ?? progress.value?.percent ?? 0)}`;
});

const resolvedCoverUrl = computed(() => resolveApiAssetUrl(book.value?.cover_url));

function formatDate(value: string) {
  return formatDateTime(value, "时间未知");
}

function formatOptionalDate(value: string | null | undefined) {
  return formatDateTime(value, "未开始");
}

function getCoverLetter(title: string) {
  const normalized = title.trim();
  return normalized ? normalized.slice(0, 1).toUpperCase() : "T";
}

function syncEditorFields(bookDetail: BookDetail) {
  editableTitle.value = bookDetail.title;
  editableAuthor.value = bookDetail.author || "";
  editableDescription.value = bookDetail.description || "";
}

async function loadBookAndChapters() {
  const [bookDetail, chapterList] = await Promise.all([
    booksApi.detail(props.bookId),
    booksApi.chapters(props.bookId),
  ]);

  book.value = bookDetail;
  chapters.value = chapterList;
  selectedRuleId.value = bookDetail.chapter_rule_id;
  syncEditorFields(bookDetail);

  booksCacheStore.set(props.bookId, {
    bookDetail,
    chapters: chapterList,
  });
}

async function loadRules() {
  rulesError.value = null;

  try {
    rules.value = await chapterRulesApi.list();

    if (!selectedRuleId.value) {
      selectedRuleId.value =
        book.value?.chapter_rule_id ??
        rules.value.find((rule) => rule.is_default)?.id ??
        rules.value[0]?.id ??
        null;
    }
  } catch (error) {
    rules.value = [];
    rulesError.value = getErrorMessage(error);
  }
}

async function loadProgress() {
  try {
    progress.value = await booksApi.getProgress(props.bookId);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      progress.value = null;
      return;
    }

    progress.value = null;
  }
}

async function loadPage() {
  loading.value = true;
  pageError.value = null;

  try {
    await loadBookAndChapters();
    await Promise.all([loadRules(), loadProgress()]);
  } catch (error) {
    book.value = null;
    chapters.value = [];
    progress.value = null;
    pageError.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
}

function reloadPage() {
  void loadPage();
}

function goBack() {
  void router.push({ name: "books" });
}

function goToChapter(chapterIndex: number) {
  void router.push({
    name: "reader",
    params: {
      bookId: props.bookId,
      chapterIndex,
    },
  });
}

function openCatalog() {
  catalogVisible.value = true;
}

function openEditor() {
  if (!book.value) {
    return;
  }

  syncEditorFields(book.value);
  editorVisible.value = true;
}

function handleCatalogSelect(chapterIndex: number) {
  catalogVisible.value = false;
  goToChapter(chapterIndex);
}

async function handleReadAction() {
  readingPending.value = true;

  try {
    if (!progress.value) {
      goToChapter(0);
      return;
    }

    goToChapter(progress.value.chapter_index);
  } finally {
    readingPending.value = false;
  }
}

async function handleSaveMetadata() {
  if (!book.value) {
    return;
  }

  metadataSaving.value = true;

  try {
    await booksApi.updateMetadata(book.value.id, {
      title: editableTitle.value.trim() || null,
      author: editableAuthor.value.trim() || null,
      description: editableDescription.value.trim() || null,
    });
    const refreshed = await booksApi.detail(book.value.id);
    book.value = refreshed;
    syncEditorFields(refreshed);
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent(BOOK_METADATA_UPDATED_EVENT, { detail: { bookId: book.value.id } }));
    }
    editorVisible.value = false;
    notify.success("书籍信息已保存");
  } catch (error) {
    notify.error(getErrorMessage(error));
  } finally {
    metadataSaving.value = false;
  }
}

const coverInputRef = ref<HTMLInputElement | null>(null);

async function handleCoverUpload(event: Event) {
  if (!book.value) {
    return;
  }

  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!(file instanceof File)) {
    notify.error("未找到可上传的封面文件");
    return;
  }

  coverUploading.value = true;

  try {
    const updated = await booksApi.uploadCover(book.value.id, file);
    book.value = updated;
    notify.success("封面已更新");
  } catch (error) {
    notify.error(getErrorMessage(error));
  } finally {
    coverUploading.value = false;
    if (coverInputRef.value) {
      coverInputRef.value.value = "";
    }
  }
}

async function handleRemoveCover() {
  if (!book.value) {
    return;
  }

  coverDeleting.value = true;

  try {
    await booksApi.deleteCover(book.value.id);
    const refreshed = await booksApi.detail(book.value.id);
    book.value = refreshed;
    notify.success("封面已删除");
  } catch (error) {
    notify.error(getErrorMessage(error));
  } finally {
    coverDeleting.value = false;
  }
}

async function handleReparse() {
  if (!selectedRuleId.value) {
    notify.info("请先选择一个目录规则");
    return;
  }

  reparsePending.value = true;

  try {
    await booksApi.reparse(props.bookId, selectedRuleId.value);
    notify.success("目录已重新解析");
    await loadBookAndChapters();
  } catch (error) {
    notify.error(getErrorMessage(error));
  } finally {
    reparsePending.value = false;
  }
}

watch(
  () => props.bookId,
  () => {
    catalogVisible.value = false;
    editorVisible.value = false;
    void loadPage();
  },
  { immediate: true },
);
</script>

<style scoped>
.book-detail-page {
  display: grid;
  gap: 24px;
}

.book-detail-page__topbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.book-detail-page__crumb {
  color: var(--text-secondary);
  font-size: 13px;
}

.book-detail-page__loading {
  display: grid;
  gap: 18px;
}

.book-detail-page__loading-card {
  min-height: 220px;
}

.detail-hero {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 24px;
  padding: clamp(24px, 4vw, 32px);
  border-radius: 28px;
  /* 二次元风格英雄区：淡蓝粉光晕 + 奶白底色 */
  background:
    radial-gradient(circle at top right, rgba(74, 159, 217, 0.18), transparent 26%),
    radial-gradient(circle at bottom left, rgba(244, 164, 180, 0.16), transparent 32%),
    color-mix(in srgb, var(--surface-color) 94%, white 6%);
  box-shadow: var(--surface-shadow);
}

.detail-hero__cover {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 280px;
  border-radius: 24px;
  /* 二次元 pastel 蓝粉渐变封面背景 */
  background:
    linear-gradient(155deg, rgba(74, 159, 217, 0.92), rgba(244, 164, 180, 0.92)),
    linear-gradient(180deg, rgba(255, 255, 255, 0.2), transparent);
  color: white;
  overflow: hidden;
}

.detail-hero__cover--filled {
  background: rgba(255, 255, 255, 0.7);
}

.detail-hero__cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.detail-hero__cover-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 1;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.detail-hero__cover-letter {
  position: relative;
  z-index: 1;
  font-family: var(--font-display);
  font-size: 72px;
  font-weight: 700;
}

.detail-hero__body {
  display: grid;
  gap: 18px;
  align-content: center;
}

.detail-hero__eyebrow {
  display: inline-flex;
  width: fit-content;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(74, 159, 217, 0.16);
  color: var(--primary-color);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detail-hero__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(30px, 4vw, 46px);
  line-height: 1.08;
}

.detail-hero__author {
  margin: 0;
  color: var(--text-secondary);
  font-size: 18px;
}

.detail-hero__description {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
  white-space: pre-wrap;
}

.detail-hero__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.detail-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.detail-card__heading {
  font-weight: 700;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-color-soft);
}

.detail-card {
  border: 1px solid var(--border-color-soft);
  border-radius: var(--radius-xl);
  background: var(--surface-raised);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.detail-card--full {
  grid-column: 1 / -1;
}

.detail-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.detail-info-item {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.55);
}

.detail-info-item--wide {
  grid-column: 1 / -1;
}

.detail-info-item span {
  display: block;
  color: var(--text-secondary);
  font-size: 12px;
}

.detail-info-item strong {
  display: block;
  margin-top: 6px;
  line-height: 1.6;
}

.detail-info-item__multiline {
  white-space: pre-wrap;
}

.detail-group-list {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.55);
}

.detail-group-list__label,
.detail-file-path__label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 12px;
}

.detail-group-list__tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-file-path {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.55);
}

.detail-file-path code {
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--text-primary);
}

.detail-rule-card {
  display: grid;
  gap: 16px;
}

.detail-rule-card__current span {
  display: block;
  color: var(--text-secondary);
  font-size: 12px;
}

.detail-rule-card__current strong {
  display: block;
  margin-top: 6px;
  font-size: 18px;
}

.detail-rule-card__current p {
  margin: 10px 0 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.detail-rule-card__alert {
  border-radius: 16px;
}

.detail-rule-card__actions {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
}

.metadata-modal {
  border-radius: 24px;
}

.metadata-modal__layout {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 20px;
}

.metadata-modal__cover-panel {
  display: grid;
  gap: 14px;
}

.metadata-modal__cover {
  display: grid;
  place-items: center;
  min-height: 280px;
  border-radius: 22px;
  border: 1px solid rgba(74, 159, 217, 0.22);
  /* 二次元 pastel 蓝白渐变 */
  background: linear-gradient(180deg, #F0F8FF 0%, #E0E8F0 100%);
  overflow: hidden;
  color: var(--text-secondary);
}

.metadata-modal__cover--filled {
  background: rgba(255, 255, 255, 0.72);
}

.metadata-modal__cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.metadata-modal__cover-type {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--primary-color);
}

.metadata-modal__cover-letter {
  font-family: var(--font-display);
  font-size: 68px;
  line-height: 1;
}

.metadata-modal__cover-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.metadata-modal__cover-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.metadata-modal__form {
  display: grid;
  gap: 16px;
}

.metadata-modal__field {
  display: grid;
  gap: 8px;
}

.metadata-modal__textarea {
  width: 100%;
  min-height: 120px;
  padding: 10px 12px;
  border: 1px solid var(--border-color-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.72);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 14px;
  line-height: 1.7;
  resize: vertical;
  outline: none;
  transition: border-color 160ms ease;
}
.metadata-modal__textarea:focus {
  border-color: var(--accent-color);
}

.metadata-modal__field span {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.metadata-modal__footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 960px) {
  .detail-hero,
  .detail-grid,
  .metadata-modal__layout {
    grid-template-columns: 1fr;
  }

  .detail-hero__cover {
    min-height: 220px;
  }
}

@media (max-width: 720px) {
  .book-detail-page__topbar,
  .detail-hero__actions,
  .detail-rule-card__actions,
  .detail-info-grid,
  .metadata-modal__footer {
    display: grid;
    grid-template-columns: 1fr;
  }

  .detail-info-item--wide {
    grid-column: auto;
  }
}
</style>
