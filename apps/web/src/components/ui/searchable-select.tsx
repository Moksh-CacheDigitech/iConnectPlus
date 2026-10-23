"use client";

import { useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ChevronDown } from "lucide-react";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export type SearchableSelectOption = {
  value: string;
  label: string;
  description?: string;
  disabled?: boolean;
};

type SearchableSelectProps = {
  value: string;
  onChange: (value: string) => void;
  options: SearchableSelectOption[];
  placeholder?: string;
  searchPlaceholder?: string;
  className?: string;
  disabled?: boolean;
  /** Allow keeping a value that is not in the options list (legacy data). */
  allowCustomValue?: boolean;
  /** When false, hide the in-menu search field (short lists). Default true. */
  searchable?: boolean;
};

/**
 * CRM-style searchable dropdown: trigger + popover list
 * (`rounded-lg border border-border bg-popover shadow-md`).
 */
export function SearchableSelect({
  value,
  onChange,
  options,
  placeholder = "Select…",
  searchPlaceholder = "Search…",
  className,
  disabled,
  allowCustomValue = true,
  searchable = true,
}: SearchableSelectProps) {
  const listId = useId();
  const triggerRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [query, setQuery] = useState("");
  const [highlight, setHighlight] = useState(0);
  const [coords, setCoords] = useState<{
    top: number;
    left: number;
    width: number;
  } | null>(null);

  const selected = options.find((o) => o.value === value);
  const displayLabel = selected?.label || (allowCustomValue && value ? value : "") || placeholder;

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return options;
    return options.filter(
      (o) =>
        o.label.toLowerCase().includes(q) ||
        o.value.toLowerCase().includes(q) ||
        (o.description ?? "").toLowerCase().includes(q),
    );
  }, [options, query]);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!open) return;
    setQuery("");
    setHighlight(0);
    if (!searchable) return;
    const t = window.setTimeout(() => searchRef.current?.focus(), 20);
    return () => window.clearTimeout(t);
  }, [open, searchable]);

  useEffect(() => {
    setHighlight(0);
  }, [query]);

  const updatePosition = useCallback(() => {
    const trigger = triggerRef.current;
    if (!trigger) return;
    const rect = trigger.getBoundingClientRect();
    const menu = menuRef.current;
    const menuHeight = menu?.offsetHeight || 220;
    const gap = 4;
    const pad = 8;

    let top = rect.bottom + gap;
    if (top + menuHeight > window.innerHeight - pad) {
      top = Math.max(pad, rect.top - gap - menuHeight);
    }

    const width = Math.min(Math.max(rect.width, 200), window.innerWidth - pad * 2);
    let left = rect.left;
    left = Math.min(Math.max(pad, left), window.innerWidth - width - pad);
    setCoords({ top, left, width });
  }, []);

  useLayoutEffect(() => {
    if (!open) {
      setCoords(null);
      return;
    }
    updatePosition();
    const id = requestAnimationFrame(() => updatePosition());
    return () => cancelAnimationFrame(id);
  }, [open, updatePosition, filtered.length, query]);

  useEffect(() => {
    if (!open) return;

    function onDoc(e: MouseEvent) {
      const t = e.target as Node;
      if (triggerRef.current?.contains(t) || menuRef.current?.contains(t)) return;
      setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }

    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [open, updatePosition]);

  function pick(next: string) {
    onChange(next);
    setOpen(false);
  }

  function onSearchKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, Math.max(0, filtered.length - 1)));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      const hit = filtered[highlight];
      if (hit && !hit.disabled) pick(hit.value);
      else if (allowCustomValue && query.trim()) pick(query.trim());
    }
  }

  return (
    <div className={cn("relative min-w-0", className)}>
      <button
        ref={triggerRef}
        type="button"
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        title={displayLabel}
        className={cn(
          "flex h-8.5 w-full cursor-pointer items-center justify-between gap-2 rounded-lg border border-input/80 bg-background/60 px-3 text-left text-sm outline-none transition-all duration-150",
          "hover:bg-muted/20",
          "focus-visible:border-primary/60 focus-visible:ring-3 focus-visible:ring-primary/15",
          "shadow-[0_1px_2px_0_rgba(0,0,0,0.02)] backdrop-blur-xs",
          open && "border-ring ring-3 ring-ring/50",
          "disabled:cursor-not-allowed disabled:opacity-50",
        )}
        onClick={() => setOpen((v) => !v)}
      >
        <span className={cn("min-w-0 truncate", !value && "text-muted-foreground")}>
          {displayLabel}
        </span>
        <ChevronDown
          className={cn(
            "size-4 shrink-0 text-muted-foreground transition-transform duration-200",
            open && "rotate-180",
          )}
        />
      </button>

      {mounted && open
        ? createPortal(
          <div
            ref={menuRef}
            id={listId}
            className="fixed z-[200] overflow-hidden rounded-lg border border-border bg-popover shadow-md"
            style={{
              top: coords?.top ?? 0,
              left: coords?.left ?? 0,
              width: coords?.width ?? 220,
              visibility: coords ? "visible" : "hidden",
            }}
          >
            {searchable ? (
              <div className="border-b border-border/80 p-2">
                <Input
                  ref={searchRef}
                  value={query}
                  placeholder={searchPlaceholder}
                  className="h-8"
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={onSearchKeyDown}
                  onMouseDown={(e) => e.stopPropagation()}
                />
              </div>
            ) : null}
            <ul
              role="listbox"
              aria-label={placeholder}
              className="max-h-48 overflow-y-auto py-1"
            >
              {filtered.length === 0 ? (
                <li className="px-3 py-2 text-xs text-muted-foreground">No matches</li>
              ) : (
                filtered.map((opt, i) => {
                  const active = opt.value === value;
                  const focused = i === highlight;
                  return (
                    <li key={opt.value || `__empty_${i}`}>
                      <button
                        type="button"
                        role="option"
                        aria-selected={active}
                        disabled={opt.disabled}
                        title={opt.label}
                        className={cn(
                          "flex w-full cursor-pointer flex-col px-3 py-1.5 text-left text-sm transition-colors duration-200 hover:bg-muted/80",
                          active && "bg-muted/60 font-medium",
                          focused && !active && "bg-muted/40",
                          opt.disabled && "cursor-not-allowed opacity-50",
                        )}
                        onMouseEnter={() => setHighlight(i)}
                        onMouseDown={(e) => e.preventDefault()}
                        onClick={() => {
                          if (!opt.disabled) pick(opt.value);
                        }}
                      >
                        <span className="min-w-0 truncate">{opt.label}</span>
                        {opt.description ? (
                          <span className="mt-0.5 line-clamp-2 text-[10px] leading-snug text-muted-foreground">
                            {opt.description}
                          </span>
                        ) : null}
                      </button>
                    </li>
                  );
                })
              )}
            </ul>
          </div>,
          document.body,
        )
        : null}
    </div>
  );
}
