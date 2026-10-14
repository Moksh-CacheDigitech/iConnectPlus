"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

import { Input } from "@/components/ui/input";
import { filterShellHits, type ShellSearchHit } from "@/lib/shell-search";
import { cn } from "@/lib/utils";

type ModulePaneSearchProps = {
  placeholder: string;
  panes: readonly ShellSearchHit[];
  className?: string;
  /** Open results from the first character (home module finder). */
  minChars?: number;
};

/** Topbar combobox that jumps to module workspace panes (or ERP modules on home). */
export function ModulePaneSearch({
  placeholder,
  panes,
  className,
  minChars = 1,
}: ModulePaneSearchProps) {
  const router = useRouter();
  const listId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

  const hits = useMemo(() => {
    if (query.trim().length < minChars) return [] as ShellSearchHit[];
    return filterShellHits(panes, query);
  }, [panes, query, minChars]);

  useEffect(() => {
    setActiveIndex(0);
  }, [hits]);

  useEffect(() => {
    function onPointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, []);

  function goTo(hit: ShellSearchHit) {
    setOpen(false);
    setQuery("");
    router.push(hit.href);
  }

  const showPanel = open && query.trim().length >= minChars;

  return (
    <div ref={rootRef} className={cn("relative min-w-0 flex-1", className)}>
      <div className="relative mx-auto w-full max-w-xl">
        <Search
          className="pointer-events-none absolute top-1/2 left-2.5 size-3.5 -translate-y-1/2 text-muted-foreground"
          aria-hidden
        />
        <Input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={(e) => {
            if (!showPanel || hits.length === 0) {
              if (e.key === "Escape") setOpen(false);
              return;
            }
            if (e.key === "ArrowDown") {
              e.preventDefault();
              setActiveIndex((i) => (i + 1) % hits.length);
            } else if (e.key === "ArrowUp") {
              e.preventDefault();
              setActiveIndex((i) => (i - 1 + hits.length) % hits.length);
            } else if (e.key === "Enter") {
              e.preventDefault();
              const hit = hits[activeIndex];
              if (hit) goTo(hit);
            } else if (e.key === "Escape") {
              setOpen(false);
            }
          }}
          placeholder={placeholder}
          role="combobox"
          aria-expanded={showPanel}
          aria-controls={listId}
          aria-autocomplete="list"
          autoComplete="off"
          className="h-9 cursor-text rounded-lg border-border/80 bg-background/80 pr-3 pl-8 text-[13px] shadow-none transition-colors duration-150 focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/30"
        />

        {showPanel ? (
          <div
            id={listId}
            role="listbox"
            className="erp-scroll absolute top-[calc(100%+0.35rem)] left-0 z-50 max-h-[min(70vh,22rem)] w-full overflow-y-auto overscroll-contain rounded-xl border border-border/80 bg-card py-1 shadow-lg"
          >
            {hits.length === 0 ? (
              <p className="px-3 py-2.5 text-[13px] text-muted-foreground">
                No results. Try another name or keyword.
              </p>
            ) : (
              <ul className="py-0.5">
                {hits.map((hit, index) => {
                  const active = index === activeIndex;
                  return (
                    <li key={hit.id} role="option" aria-selected={active}>
                      <Link
                        href={hit.href}
                        onClick={(e) => {
                          e.preventDefault();
                          goTo(hit);
                        }}
                        onMouseEnter={() => setActiveIndex(index)}
                        className={cn(
                          "flex cursor-pointer flex-col gap-0.5 px-3 py-2 text-left transition-colors duration-150",
                          active ? "bg-accent text-accent-foreground" : "hover:bg-muted/70",
                        )}
                      >
                        <span className="truncate text-[13px] font-medium tracking-tight">
                          {hit.title}
                        </span>
                        <span className="truncate text-[11px] text-muted-foreground">
                          {hit.subtitle}
                        </span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
