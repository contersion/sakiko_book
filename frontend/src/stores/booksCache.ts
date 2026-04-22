import { defineStore } from "pinia";
import type { BookChapter, BookDetail } from "../types/api";

interface CachedBookData {
  bookDetail: BookDetail | null;
  chapters: BookChapter[] | null;
  fetchedAt: number;
}

const CACHE_TTL_MS = 5 * 60 * 1000; // 5 分钟缓存有效期

export const useBooksCacheStore = defineStore("booksCache", {
  state: () => ({
    cache: new Map<number, CachedBookData>(),
  }),

  actions: {
    get(bookId: number): CachedBookData | undefined {
      const entry = this.cache.get(bookId);
      if (!entry) {
        return undefined;
      }
      if (Date.now() - entry.fetchedAt > CACHE_TTL_MS) {
        this.cache.delete(bookId);
        return undefined;
      }
      return entry;
    },

    set(bookId: number, data: Partial<CachedBookData>) {
      const existing = this.cache.get(bookId);
      this.cache.set(bookId, {
        bookDetail: data.bookDetail ?? existing?.bookDetail ?? null,
        chapters: data.chapters ?? existing?.chapters ?? null,
        fetchedAt: Date.now(),
      });
    },

    getChapters(bookId: number): BookChapter[] | null {
      return this.get(bookId)?.chapters ?? null;
    },

    getBookDetail(bookId: number): BookDetail | null {
      return this.get(bookId)?.bookDetail ?? null;
    },

    invalidate(bookId: number) {
      this.cache.delete(bookId);
    },

    invalidateAll() {
      this.cache.clear();
    },
  },
});
