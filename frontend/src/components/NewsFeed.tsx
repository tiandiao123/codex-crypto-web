import type { NewsItem } from '../types';

interface NewsFeedProps {
  news: NewsItem[];
}

// Sidebar list of latest crypto news.
export const NewsFeed = ({ news }: NewsFeedProps) => {
  return (
    <aside className="rounded-xl border border-slate-800 bg-slate-900/70 p-4">
      <h2 className="mb-4 text-lg font-semibold text-white">最新加密新闻</h2>

      <div className="space-y-4">
        {news.length === 0 && <p className="text-sm text-slate-400">等待新闻推送...</p>}

        {news.map((item) => (
          <article key={item.id} className="border-b border-slate-800 pb-3 last:border-none last:pb-0">
            <a
              href={item.url}
              target="_blank"
              rel="noreferrer"
              className="text-sm font-medium text-cyan-300 hover:text-cyan-200"
            >
              {item.title}
            </a>
            <div className="mt-1 flex items-center justify-between text-xs text-slate-400">
              <span>{item.source}</span>
              <span>{new Date(item.publishedAt).toLocaleString('zh-CN', { hour12: false })}</span>
            </div>
          </article>
        ))}
      </div>
    </aside>
  );
};
